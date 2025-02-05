from fastapi import FastAPI
from app.routers import upload, qa

app = FastAPI()

# Include the routers
app.include_router(upload.router, prefix="/api")
app.include_router(qa.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI backend!"}
