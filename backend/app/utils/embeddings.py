from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables (including the OpenAI API key)
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default embedding model
embedding_model = "text-embedding-ada-002"

def generate_embeddings(text: str):
    """
    Generate embeddings for the given text using OpenAI's embedding models.

    Args:
        text (str): Input text to generate embeddings for.

    Returns:
        list: Embedding vector (list of floats) for the input text.

    Raises:
        ValueError: If the API call fails or if there is an error with the input.
    """
    try:
        # Clean text by removing newline characters
        clean_text = text.replace("\n", " ")

        # Request embeddings from OpenAI API
        response = openai_client.embeddings.create(
            input=[clean_text],  # List of input strings
            model=embedding_model
        )

        # Extract and return the embedding for the first input
        return response.data[0].embedding
    except Exception as e:
        raise ValueError(f"Failed to generate embeddings: {str(e)}")
