import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(question, context):
    """
    Generate an answer using OpenAI GPT-3.5/4 model based on the given context.
    """
    try:
        prompt = (
            "You are an intelligent assistant answering questions based on the provided context. "
            "If the question is general knowledge, answer it without referring to the context. "
            "If the question is specific to the provided context, answer using it. "
            "When the question contains multiple parts, break it down into sub-questions and provide answers for each part separately. "
            "Ensure your responses are clear and concise. Use the context to back your answers, and include source references when available.\n\n"
            f"Context: {context}\n\n"
            f"Question: {question}"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant answering questions based on context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def classify_query(question, context):
    """
    Classify a query as either "General Knowledge" or "Context-Specific."
    """
    try:
        prompt = (
            "You are an intelligent assistant. Based on the provided question and document context, classify the question as either:\n"
            "- 'General Knowledge' (if it can be answered without specific document context).\n"
            "- 'Context-Specific' (if it requires information from the provided document context).\n\n"
            f"Document Context: {context[:1000]}... (truncated for brevity)\n\n"
            f"Question: {question}\n\n"
            "Classification:"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant for query classification."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
