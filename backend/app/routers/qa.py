from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from app.utils.llm import generate_answer, classify_query
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

        # Step 1: Query Qdrant for combined context
        top_k = 5  # Number of results to fetch
        combined_results = search_embeddings(query_vector=[], top_k=top_k, threshold=0)  # Get combined context
        combined_context = "\n".join([
            res["payload"].get("text", res["payload"].get("content", "")) for res in combined_results
        ])

        logger.info(f"📋 Combined context length: {len(combined_context)} characters")

        # Step 2: Classify the query as general knowledge or context-specific
        classification = classify_query(question, combined_context)
        logger.info(f"🔍 Query classified as: {classification}")

        if classification == "General Knowledge":
            logger.info("🔍 General knowledge question detected. Skipping Qdrant query.")
            answer = generate_answer(question, context=None)
            return {
                "question": question,
                "answer": answer,
                "sources": []  # No sources for general queries
            }

        # Step 3: Generate embeddings for the question
        question_embedding = generate_embeddings(question)
        if not question_embedding:
            logger.error("❌ Failed to generate embeddings for the question")
            raise HTTPException(status_code=500, detail="Failed to generate question embeddings")

        logger.info(f"🔢 Generated question embedding: {question_embedding[:10]}...")

        # Step 4: Query Qdrant for the most relevant documents
        relevance_threshold = 0.7  # Set the minimum similarity score
        results = search_embeddings(query_vector=question_embedding, top_k=top_k, threshold=relevance_threshold)

        logger.info(f"🔍 Qdrant returned {len(results)} results.")

        if not results:
            logger.info("🚫 No relevant documents found. Answering generically.")
            answer = generate_answer(question, context=None)
            return {
                "question": question,
                "answer": answer,
                "sources": []
            }

        # Step 5: Extract content from relevant results
        context = "\n".join([
            res["payload"].get("text", res["payload"].get("content", ""))  
            for res in results
        ])

        logger.info(f"📌 Extracted Context (length: {len(context)} chars): {context[:200]}...")

        # Step 6: Generate an answer using OpenAI API
        answer = generate_answer(question, context)
        if not answer.strip():
            logger.error("❌ OpenAI returned an empty response")
            raise HTTPException(status_code=500, detail="Failed to generate an answer")

        logger.info(f"✅ Generated answer: {answer[:100]}...")

        # Step 7: Prepare the response with sources
        response_sources = [
            {
                "filename": res["payload"].get("filename", "Unknown"),
                "content": res["payload"].get("text", res["payload"].get("content", "Content not available"))
            }
            for res in results
        ]
        response_sources = response_sources[:3] if len(response_sources) > 3 else response_sources

        return {
            "question": question,
            "answer": answer,
            "sources": response_sources
        }

    except HTTPException as e:
        logger.error(f"🚨 HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"🚨 Unexpected error in /qa: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
