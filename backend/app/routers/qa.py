from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.llm import generate_answer

router = APIRouter()

# Define the request body model
class QuestionRequest(BaseModel):
    question: str

@router.post("/qa")
async def answer_question(request: QuestionRequest):
    """
    Endpoint to answer a question using OpenAI's API via llm.py.
    """
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        # Directly use the question without any context
        context = ""  # No context needed for simple QA

        # Call the LLM function to get an answer
        answer = generate_answer(question, context)  # Pass the question and empty context
        return {"question": question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
