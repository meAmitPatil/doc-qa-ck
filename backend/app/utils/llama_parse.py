from dotenv import load_dotenv
import asyncio
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

# Set up OpenAI embedding model
embed_model = OpenAIEmbedding()

# Initialize the semantic splitter
splitter = SemanticSplitterNodeParser(
    buffer_size=1,  # Number of overlapping sentences between chunks
    breakpoint_percentile_threshold=95,  # Semantic similarity threshold
    embed_model=embed_model
)

async def parse_pdf_with_llama(pdf_path: str) -> list:
    """
    Parses a PDF file into semantic chunks using LlamaIndex.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        list: List of semantic chunks.
    """
    try:
        # Load the document
        documents = await SimpleDirectoryReader(input_files=[pdf_path]).aload_data()
        
        # Generate semantic chunks
        nodes = splitter.get_nodes_from_documents(documents)
        chunks = [node.get_content() for node in nodes]

        if not chunks:
            raise ValueError("No chunks generated. The document might be empty or improperly formatted.")
        
        return chunks
    except Exception as e:
        raise RuntimeError(f"Error parsing PDF with SemanticSplitter: {e}")
