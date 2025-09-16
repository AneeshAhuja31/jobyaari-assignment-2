import os
import json
from pathlib import Path

from langchain_community.vectorstores import FAISS

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document


BASE_DIR = r"C:\Users\HP\OneDrive\Desktop\jobyaari-assignements\ASSIGNMENT2"


embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def load_job_data(base_dir):
    docs = []
    for category_dir in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category_dir)
        if not os.path.isdir(category_path):
            continue
        
        for file in os.listdir(category_path):
            if file.startswith("job_"):
                file_path = os.path.join(category_path, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                

                job_text = f"""
                Company: {data.get("company")}
                Title: {data.get("title")}
                Location: {data.get("location")}
                Age Limit: {data.get("age_limit")}
                Experience: {data.get("experience")}
                Salary: {data.get("salary")}
                Qualification: {data.get("qualification")}
                Last Date: {data.get("last date")}
                Details: {"; ".join(data.get("details_list", []))}
                Category: {category_dir}
                """
                

                doc = Document(
                    page_content=job_text,
                    metadata={
                        "company": data.get("company"),
                        "title": data.get("title"),
                        "category": category_dir,
                        "file": file
                    }
                )
                docs.append(doc)
    return docs














save_path = os.path.join(BASE_DIR, "faiss_index")

vectorstore = FAISS.load_local(save_path, embedding_model, allow_dangerous_deserialization=True)

query = "diploma jobs in Himachal Pradesh"
results = vectorstore.similarity_search(query, k=3)

for i, res in enumerate(results, start=1):
    print(f"\nResult {i}:")
    print(res.page_content)
    print("Metadata:", res.metadata)
