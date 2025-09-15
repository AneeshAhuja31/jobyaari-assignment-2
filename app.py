import os
import streamlit as st
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Literal


FAISS_DIR = os.getenv("FAISS_DIR", os.path.join(os.getcwd(), "faiss_index"))
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GEMINI_MODEL_NAME = "gemini-2.5-flash"


class ChatState(TypedDict):
    question: str
    chat_history: List
    answer: str
    route: Literal["general", "jobs"]


def load_vectorstore(faiss_dir: str, embedding_model_name: str):
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    return FAISS.load_local(faiss_dir, embeddings, allow_dangerous_deserialization=True)

def make_gemini_llm(temperature: float = 0.2):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY environment variable not set.")
    os.environ["GEMINI_API_KEY"] = api_key
    return ChatGoogleGenerativeAI(model=GEMINI_MODEL_NAME, temperature=temperature)

def build_system_prompt():
    return (
        "You are JobYaari assistant. "
        "For questions about jobs, you MUST use the retrieved dataset. "
        "Otherwise, just answer generally without retrieval. "
        "When using job data, give structured fields: "
        "(Title, Company, Location, Experience, Qualification, Salary, Last Date, Details)."
    )


def router_node(state: ChatState, llm: ChatGoogleGenerativeAI):
    """Classify query type."""
    prompt = (
        "Classify the user query as 'general' (no job data needed) or 'jobs' "
        "(needs job retrieval). Respond with ONLY one word: general or jobs.\n\n"
        f"Query: {state['question']}"
    )
    resp = llm.invoke([HumanMessage(content=prompt)])
    route = resp.content.strip().lower()
    if route not in ["general", "jobs"]:
        route = "general"
    state["route"] = route
    return state

def general_node(state: ChatState, llm: ChatGoogleGenerativeAI):
    """Answer without retrieval."""
    system_prompt = build_system_prompt()
    result = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["question"])
    ])
    state["answer"] = result.content
    return state

def jobs_node(state: ChatState, llm: ChatGoogleGenerativeAI, vectordb: FAISS):
    """Answer with retrieval."""
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    response = conv_chain({
        "question": state["question"],
        "chat_history": state["chat_history"]
    })
    state["answer"] = response.get("answer", "")
    return state


st.set_page_config(page_title="JobYaari Chatbot", layout="wide")
st.title("💼 JobYaari Chatbot")

with st.sidebar:
    st.header("Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2)

@st.cache_resource(show_spinner=True)
def load_resources():
    return load_vectorstore(FAISS_DIR, EMBEDDING_MODEL_NAME)

try:
    vectordb = load_resources()
except Exception as e:
    st.error(f"Error loading FAISS index: {e}")
    st.stop()

try:
    llm = make_gemini_llm(temperature=temperature)
except Exception as e:
    st.error(str(e))
    st.stop()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_query := st.chat_input("Ask about jobs..."):
    st.session_state.chat_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    state: ChatState = {
        "question": user_query,
        "chat_history": [
            (m["role"], m["content"])
            for m in st.session_state.chat_messages
            if m["role"] in ["user", "assistant"]
        ],
        "answer": "",
        "route": "general",
    }

    workflow = StateGraph(ChatState)
    workflow.add_node("router", lambda s: router_node(s, llm))
    workflow.add_node("general", lambda s: general_node(s, llm))
    workflow.add_node("jobs", lambda s: jobs_node(s, llm, vectordb))

    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        lambda s: s["route"],
        {"general": "general", "jobs": "jobs"}
    )
    workflow.add_edge("general", END)
    workflow.add_edge("jobs", END)

    app = workflow.compile()

    with st.spinner("🤖 Thinking..."):
        final_state = app.invoke(state)

    answer = final_state["answer"]
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
