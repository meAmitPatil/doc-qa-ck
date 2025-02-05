import openai

openai.api_key = "your_openai_api_key"  # Replace with environment variable in production

def generate_embeddings(text: str):
    """Generate embeddings for a given text using OpenAI."""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]
