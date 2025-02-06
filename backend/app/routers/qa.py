from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.llm import generate_answer
from app.utils.embeddings import generate_embeddings
from app.utils.qdrant_client import search_embeddings

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/qa")
async def answer_question(request: QuestionRequest):
    """
    Answer a question using OpenAI's API with context retrieved from Qdrant.
    """
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        # Step 1: Embed the question
        question_embedding = generate_embeddings(question)

        # Step 2: Query Qdrant for the most relevant documents
        top_k = 5  # Number of relevant documents to retrieve
        results = search_embeddings(query_vector=question_embedding, top_k=top_k)

        # Step 3: Combine the retrieved content as context
        context = "\n".join([res["payload"].get("content", "") for res in results if "content" in res["payload"]])

        if not context.strip():
            raise HTTPException(status_code=404, detail="No relevant context found in the database.")

        # Step 4: Generate an answer using the context and question
        answer = generate_answer(question, context)
        return {"question": question, "answer": answer, "context": context}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
