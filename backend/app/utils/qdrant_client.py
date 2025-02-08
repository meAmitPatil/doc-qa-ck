import os
import uuid
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# Load environment variables
load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    logger.info("Successfully connected to Qdrant.")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {e}")
    raise e  # Stop execution if Qdrant connection fails

COLLECTION_NAME = "docs"

def initialize_qdrant(vector_size: int):
    """Initialize or reset the Qdrant collection with the specified vector size."""
    try:
        logger.info(f"Initializing Qdrant collection '{COLLECTION_NAME}' with vector size {vector_size}...")
        
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info(f"✅ Collection '{COLLECTION_NAME}' successfully initialized.")
    except Exception as e:
        logger.error(f"Error initializing Qdrant collection: {e}")

def store_embeddings(embeddings: list, payloads: list):
    """Store embeddings and metadata in Qdrant."""
    try:
        if not embeddings or not payloads:
            logger.warning("⚠️ No embeddings or payloads provided for storage.")
            return
        
        points = [
            PointStruct(
                id=payload.get("id", str(uuid.uuid4())),
                vector=embedding,
                payload=payload
            )
            for embedding, payload in zip(embeddings, payloads)
        ]
        
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"✅ Stored {len(points)} embeddings in the collection '{COLLECTION_NAME}'.")
    except Exception as e:
        logger.error(f"Error storing embeddings in Qdrant: {e}")

def search_embeddings(query_vector, top_k: int, threshold: float = 0.7):
    """Search Qdrant for the most relevant embeddings with a confidence threshold."""
    try:
        if not query_vector:
            logger.warning("⚠️ Query vector is empty. Cannot perform search.")
            return []
        
        logger.info(f"🔍 Searching Qdrant for top {top_k} matches...")

        # Perform vector search
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k
        )

        if not results:
            logger.warning("⚠️ No matching results found in Qdrant.")
            return []
        
        # **Filter results based on threshold score**
        filtered_results = [
            {"score": res.score, "payload": res.payload} for res in results if res.score >= threshold
        ]

        if not filtered_results:
            logger.info("🚫 No documents met the relevance threshold.")
            return []  # Return an empty list if nothing is relevant

        logger.info(f"✅ Found {len(filtered_results)} highly relevant documents.")
        return filtered_results

    except Exception as e:
        logger.error(f"❌ Error searching embeddings in Qdrant: {e}")
        return []

