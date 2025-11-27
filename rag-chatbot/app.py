
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient, models
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

QDRANT_CLUSTER_URL = os.getenv("QDRANT_CLUSTER_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = QdrantClient(
    url=QDRANT_CLUSTER_URL,
    api_key=QDRANT_API_KEY,
)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

COLLECTION_NAME = "hira_book_2025"

class QueryRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    # Ensure the docs directory exists
    docs_path = "../docs"
    if not os.path.exists(docs_path):
        raise HTTPException(status_code=500, detail=f"Docs directory not found at {docs_path}")

    # Create collection if it doesn't exist
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
        )
    except Exception as e:
        print(f"Collection {COLLECTION_NAME} might already exist or there was an error creating it: {e}")

    # Load markdown files and create embeddings
    points = []
    for root, _, files in os.walk(docs_path):
        for file_name in files:
            if file_name.endswith(".md"):
                file_path = os.path.join(root, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                response = openai_client.embeddings.create(
                    input=content,
                    model="text-embedding-ada-002"
                )
                embedding = response.data[0].embedding

                points.append(
                    models.PointStruct(
                        id=len(points),
                        vector=embedding,
                        payload={"file_path": file_path, "content": content}
                    )
                )

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        ).wait()
        print(f"Upserted {len(points)} points to Qdrant collection {COLLECTION_NAME}")
    else:
        print("No markdown files found to embed.")

@app.post("/query")
async def query_chatbot(request: QueryRequest):
    query_embedding_response = openai_client.embeddings.create(
        input=request.query,
        model="text-embedding-ada-002"
    )
    query_embedding = query_embedding_response.data[0].embedding

    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=3,
        append_vectors=True
    )

    context = "\n".join([hit.payload["content"] for hit in search_result])

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {request.query}"}
        ]
    )
    return {"answer": response.choices[0].message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
