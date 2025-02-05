from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, qa

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