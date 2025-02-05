from fastapi import APIRouter
from app.utils.qdrant_client import search_embeddings
from app.utils.embeddings import generate_embeddings

router = APIRouter()

@router.post("/qa")
async def question_answering(question: str):
    # Generate embedding for the question
    question_embedding = generate_embeddings(question)

    # Retrieve top results from Qdrant
    results = search_embeddings(query_vector=question_embedding, top_k=5)

    # For now, just return the retrieved results
    return {"results": results}
