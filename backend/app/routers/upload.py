from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import logging
from textwrap import wrap
from app.utils.embeddings import generate_embeddings
from app.utils.qdrant_client import store_embeddings
from app.utils.llama_parse import parse_pdf_with_llama  # Import async function

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

def chunk_text(text, chunk_size=1000):
    """Splits text into manageable chunks."""
    return wrap(text, width=chunk_size)

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    uploaded_file_paths = []
    success_results = []
    failed_results = []

    # Save files locally
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded_file_paths.append(file_path)
            logging.info(f"File saved successfully: {file.filename}")
        except Exception as e:
            logging.error(f"Failed to save file {file.filename}: {e}")
            failed_results.append({"file": file.filename, "error": f"Failed to save: {e}"})

    # Process each file
    for file_path in uploaded_file_paths:
        try:
            extracted_text = await parse_pdf_with_llama(file_path)  # ✅ Await async parsing

            if isinstance(extracted_text, list):
                extracted_text = "\n".join(extracted_text)

            if not extracted_text.strip():
                raise ValueError("No text extracted from the PDF. It may be scanned or corrupted.")

            # Chunk text and generate embeddings
            text_chunks = chunk_text(extracted_text)
            embeddings = [generate_embeddings(chunk) for chunk in text_chunks]

            # Store chunks in Qdrant
            for chunk, embedding in zip(text_chunks, embeddings):
                metadata = {
                    "filename": os.path.basename(file_path),
                    "content": chunk
                }
                store_embeddings([embedding], [metadata])

            success_results.append({
                "file": os.path.basename(file_path),
                "status": "Successfully processed and stored in Qdrant"
            })

            logging.info(f"--- Parsed and Stored Content for {os.path.basename(file_path)} ---")

        except Exception as e:
            failed_results.append({
                "file": os.path.basename(file_path),
                "error": f"Processing failed: {e}"
            })
            logging.error(f"Error processing {os.path.basename(file_path)}: {e}")

    return {"success": success_results, "failed": failed_results}
