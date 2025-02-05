from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)  # Update if running Qdrant on a different host

COLLECTION_NAME = "docs"

def initialize_qdrant(vector_size: int):
    """Ensure the collection exists in Qdrant."""
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

def store_embeddings(embeddings: list, payloads: list):
    """Store embeddings in Qdrant."""
    points = [{"vector": embedding, "payload": payload} for embedding, payload in zip(embeddings, payloads)]
    client.upsert(collection_name=COLLECTION_NAME, points=points)

def search_embeddings(query_vector, top_k: int):
    """Retrieve top-k results from Qdrant."""
    results = client.search(collection_name=COLLECTION_NAME, query_vector=query_vector, limit=top_k)
    return [{"score": res.score, "payload": res.payload} for res in results]
