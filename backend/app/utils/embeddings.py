from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

embedding_model = "text-embedding-ada-002"

def generate_embeddings(text: str):
    try:
        clean_text = text.replace("\n", " ")

        response = openai_client.embeddings.create(
            input=[clean_text],
            model=embedding_model
        )

        # Extract embeddings properly
        embeddings = response.data[0].embedding

        return embeddings
    except Exception as e:
        raise ValueError(f"Failed to generate embeddings: {str(e)}")

