import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

COLLECTION_NAME = "docs"

def initialize_qdrant(vector_size: int):
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' initialized in Qdrant Cloud.")

def store_embeddings(embeddings: list, payloads: list):
    points = [
        PointStruct(
            id=payload.get("id", str(uuid.uuid4())),
            vector=embedding,
            payload=payload
        )
        for embedding, payload in zip(embeddings, payloads)
    ]
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} embeddings in the collection '{COLLECTION_NAME}'.")

def search_embeddings(query_vector, top_k: int):
    results = qdrant_client.search(collection_name=COLLECTION_NAME, query_vector=query_vector, limit=top_k)
    return [{"score": res.score, "payload": res.payload} for res in results]
