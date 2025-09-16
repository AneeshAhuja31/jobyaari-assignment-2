import os
import json
import time
from pathlib import Path
from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
from langchain.embeddings import HuggingFaceEmbeddings


BASE_DIR = r"C:\Users\HP\OneDrive\Desktop\jobyaari-assignements\ASSIGNMENT2"
MONGODB_URI = os.getenv("MONGODB_ATLAS_URI")
DB_NAME = "jobyaari"
COLLECTION_NAME = "jobs"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_NAME = "job_index"
EMBEDDING_FIELD = "job_embedding"


client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)



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

                docs.append({
                    "company": data.get("company"),
                    "title": data.get("title"),
                    "category": category_dir,
                    "file": file,
                    "text": job_text
                })
    return docs



def create_vector_index():
    search_index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": EMBEDDING_FIELD,
                    "numDimensions": 384,
                    "similarity": "cosine"
                },
                {"type": "filter", "path": "category"},
                {"type": "filter", "path": "title"}
            ]
        },
        name=INDEX_NAME,
        type="vectorSearch"
    )

    result = collection.create_search_index(model=search_index_model)
    print("New search index named " + result + " is building.")


    print("⏳ Waiting for index to be ready...")
    predicate = lambda idx: idx.get("queryable") is True
    while True:
        indices = list(collection.list_search_indexes(INDEX_NAME))
        if len(indices) and predicate(indices[0]):
            break
        time.sleep(5)
    print(f"✅ Index {INDEX_NAME} is ready for querying.")



def ingest_jobs():
    jobs = load_job_data(BASE_DIR)
    print(f"Loaded {len(jobs)} jobs")

    for job in jobs:
        vector = embedding_model.embed_query(job["text"])
        job_doc = {
            **job,
            EMBEDDING_FIELD: vector
        }
        collection.insert_one(job_doc)

    print(f"✅ Inserted {len(jobs)} job documents into MongoDB Atlas")


if __name__ == "__main__":
    create_vector_index()
    ingest_jobs()
    client.close()
