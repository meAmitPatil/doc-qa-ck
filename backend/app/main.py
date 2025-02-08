from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, qa
from app.utils.qdrant_client import qdrant_client, COLLECTION_NAME, initialize_qdrant
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware to handle requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your production frontend URL
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers for different API endpoints
app.include_router(upload.router, prefix="/api")  # Handles file uploads
app.include_router(qa.router, prefix="/api")      # Handles Q&A related functionality

# Root endpoint for API status check
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI backend!"}

@app.on_event("startup")
async def startup_event():
    """
    Clears Qdrant on server restart and recreates the collection.
    """
    try:
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
        logger.info("🗑️ Cleared Qdrant collection on startup.")

        # Recreate collection immediately
        vector_size = 1536  # Update based on OpenAI model
        initialize_qdrant(vector_size)
        logger.info(f"✅ Recreated Qdrant collection '{COLLECTION_NAME}' on startup.")
    except Exception as e:
        logger.error(f"❌ Failed to clear/recreate Qdrant on startup: {e}")

@app.get("/clear-qdrant")
async def clear_qdrant():
    """API route to manually clear Qdrant (called when user refreshes site)."""
    try:
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
        logger.info("🗑️ Cleared Qdrant collection via API request.")

        # Recreate collection immediately
        vector_size = 1536  # Ensure correct embedding size
        initialize_qdrant(vector_size)
        logger.info(f"✅ Recreated Qdrant collection via API request.")

        return {"message": "🗑️ Cleared and recreated Qdrant successfully."}
    except Exception as e:
        logger.error(f"❌ Failed to clear Qdrant via API: {e}")
        return {"error": str(e)}