from dotenv import load_dotenv
import asyncio
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

load_dotenv()

# Initialize LlamaParse
parser = LlamaParse(result_type="text")  # "markdown" or "text"

async def parse_pdf_with_llama(pdf_path: str) -> str:
    """Parses a PDF file and extracts text using LlamaParse (async)."""
    try:
        # Use `aload_data()` for async parsing
        documents = await SimpleDirectoryReader(input_files=[pdf_path], file_extractor={".pdf": parser}).aload_data()
        extracted_text = "\n".join([doc.text for doc in documents])  # Concatenate extracted text

        if not extracted_text.strip():
            raise ValueError("No text extracted from the PDF. It may be scanned or corrupted.")
        
        return extracted_text
    except Exception as e:
        raise RuntimeError(f"Error parsing PDF with LlamaParse: {e}")
