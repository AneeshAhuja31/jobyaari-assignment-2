# JobYaari Chatbot Architecture

This diagram shows the complete flow from web scraping to the intelligent chatbot implementation.

```mermaid
graph TD
    %% Data Sources
    A[JobYaari Website] --> B{Job Categories}
    B --> C[Education Jobs]
    B --> D[Engineering Jobs]  
    B --> E[Science Jobs]
    B --> F[Commerce Jobs]

    %% Step 1: Link Extraction
    C --> G[education_links.py]
    D --> H[engineering_links.py]
    E --> I[science_links.py]
    F --> J[commerce_links.py]

    G --> K[education_jobs_links.json]
    H --> L[engineering_jobs_links.json]
    I --> M[science_jobs_links.json]
    J --> N[commerce_jobs_links.json]

    %% Step 2: Batch Scraping
    K --> O[batch_scrape_education.py]
    L --> P[batch_scrape_engineering.py]
    M --> Q[batch_scrape_science.py]
    N --> R[batch_scrape_commerce.py]

    O --> S[education_jobs_results/]
    P --> T[engineering_jobs_results/]
    Q --> U[science_jobs_results/]
    R --> V[commerce_jobs_results/]

    S --> W[job_1.json, job_2.json, ...]
    T --> X[job_1.json, job_2.json, ...]
    U --> Y[job_1.json, job_2.json, ...]
    V --> Z[job_1.json, job_2.json, ...]

    %% Step 3: Data Processing & Embedding
    W --> AA[ingestion.py]
    X --> AA
    Y --> AA
    Z --> AA

    AA --> BB[HuggingFaceEmbeddings<br/>sentence-transformers/all-MiniLM-L6-v2]
    AA --> CC[LangChain Documents<br/>with metadata]
    
    BB --> DD[FAISS Vector Store]
    CC --> DD
    DD --> EE[faiss_index/]

    %% Alternative: MongoDB Atlas Vector Search
    AA --> FF[ingestion2.py]
    FF --> GG[MongoDB Atlas<br/>Vector Search]
    BB --> GG

    %% Step 4: Chatbot Application
    EE --> HH[app.py - Streamlit App]
    
    HH --> II{LangGraph Workflow}
    II --> JJ[Router Node<br/>Query Classification]
    
    JJ --> KK{Route Decision}
    KK -->|general| LL[General Node<br/>Direct LLM Response]
    KK -->|jobs| MM[Jobs Node<br/>RAG with Vector Search]
    
    MM --> NN[FAISS Retriever<br/>Top-K Similarity Search]
    NN --> OO[ConversationalRetrievalChain]
    
    LL --> PP[Gemini 2.5 Flash LLM]
    OO --> PP
    
    PP --> QQ[Final Response]
    QQ --> RR[Streamlit Chat Interface]

    %% Styling
    classDef scraping fill:#e1f5fe
    classDef data fill:#f3e5f5
    classDef embedding fill:#e8f5e8
    classDef chatbot fill:#fff3e0
    classDef llm fill:#ffebee

    class G,H,I,J,O,P,Q,R scraping
    class K,L,M,N,S,T,U,V,W,X,Y,Z data
    class AA,BB,CC,DD,EE,FF,GG embedding
    class HH,II,JJ,KK,LL,MM,NN,OO,RR chatbot
    class PP llm
```

## Architecture Components

### 🕷️ **Data Collection Phase**
- Selenium-based scrapers for each job category
- Batch processing for detailed job extraction
- JSON storage organized by category

### 🔄 **Data Processing Phase** 
- Document creation with LangChain
- HuggingFace embeddings generation
- FAISS/MongoDB vector storage

### 🤖 **Chatbot Phase**
- LangGraph workflow orchestration
- Intelligent query routing
- RAG implementation with vector search
- Gemini LLM integration