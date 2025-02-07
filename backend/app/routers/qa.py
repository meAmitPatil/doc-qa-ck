from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from app.utils.llm import generate_answer
from app.utils.embeddings import generate_embeddings
from app.utils.qdrant_client import search_embeddings

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.error("❌ Received empty question")
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        logger.info(f"✅ Received question: {question}")

        # Step 1: Generate embeddings for the question
        question_embedding = generate_embeddings(question)
        if not question_embedding:
            logger.error("❌ Failed to generate embeddings for the question")
            raise HTTPException(status_code=500, detail="Failed to generate question embeddings")

        logger.info(f"🔢 Generated question embedding: {question_embedding[:10]}...")  # Print first 10 values

        # Step 2: Query Qdrant for the most relevant documents
        top_k = 5  # Increase this value if needed
        results = search_embeddings(query_vector=question_embedding, top_k=top_k)

        logger.info(f"🔍 Qdrant returned {len(results)} results.")
        for i, res in enumerate(results):
            logger.info(f"📌 Document {i+1} Payload: {res['payload']}")  # Log full payload

        # Step 3: Extract content (detect correct key dynamically)
        context = "\n".join([
            res["payload"].get("text", res["payload"].get("content", ""))  # Try "text" first, fallback to "content"
            for res in results
        ])

        logger.info(f"📌 Extracted Context (length: {len(context)} chars): {context[:200]}...")  # Print first 200 chars

        if not context.strip():
            logger.warning("⚠️ No relevant context found in Qdrant. Check if 'text' or 'content' is the correct key.")
            raise HTTPException(status_code=404, detail="No relevant context found in the database.")

        # Step 4: Generate an answer using OpenAI API
        answer = generate_answer(question, context)

        if not answer.strip():
            logger.error("❌ OpenAI returned an empty response")
            raise HTTPException(status_code=500, detail="Failed to generate an answer")

        logger.info(f"✅ Generated answer: {answer[:100]}...")  # Print first 100 chars

        # Prepare the response
        response = {
            "question": question,
            "answer": answer,
            "context": context,
            "sources": results  # Include the sources in the response
        }

        return response

    except HTTPException as e:
        logger.error(f"🚨 HTTP Exception: {e.detail}")
        raise e  # Reraise FastAPI HTTP exceptions to return proper response

    except Exception as e:
        logger.exception(f"🚨 Unexpected error in /qa: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
