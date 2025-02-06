import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# Load environment variables
load_dotenv()

# Fetch API key and URL from the environment variables
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

# Initialize Qdrant Cloud client
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

COLLECTION_NAME = "docs"

def initialize_qdrant(vector_size: int):
    """
    Ensure the collection exists in Qdrant Cloud.
    If it doesn't exist, create it with the given vector size and cosine distance metric.
    """
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' initialized in Qdrant Cloud.")

def store_embeddings(embeddings: list, payloads: list):
    """
    Store embeddings in Qdrant Cloud with unique IDs for each point.
    
    Args:
        embeddings (list): List of embedding vectors to store.
        payloads (list): List of metadata dictionaries corresponding to the embeddings.
    """
    points = [
        PointStruct(
            id=payload.get("id", str(uuid.uuid4())),  # Use 'id' from metadata or generate a UUID
            vector=embedding,
            payload=payload
        )
        for embedding, payload in zip(embeddings, payloads)
    ]
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} embeddings in the collection '{COLLECTION_NAME}'.")

def search_embeddings(query_vector, top_k: int):
    """
    Retrieve top-k results from Qdrant Cloud based on the query vector.
    
    Args:
        query_vector (list): The query embedding vector.
        top_k (int): Number of top results to retrieve.
    
    Returns:
        list: A list of dictionaries containing scores and payloads for the top-k results.
    """
    results = qdrant_client.search(collection_name=COLLECTION_NAME, query_vector=query_vector, limit=top_k)
    return [{"score": res.score, "payload": res.payload} for res in results]
