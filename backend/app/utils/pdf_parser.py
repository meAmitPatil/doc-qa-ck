from PyPDF2 import PdfReader
import io

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from a PDF given its bytes."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        all_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
        return "\n".join(all_text)
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")