from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from app.utils.pdf_parser import extract_text_from_pdf 
from app.utils.embeddings import generate_embeddings
from app.utils.qdrant_client import store_embeddings
import logging

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    uploaded_file_paths = []
    success_results = []
    failed_results = []

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

    for file_path in uploaded_file_paths:
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
                extracted_text = extract_text_from_pdf(pdf_bytes)
                
                if not extracted_text.strip():
                    raise ValueError("No text extracted from the PDF. It may be scanned or corrupted.")
                
                # Generate embeddings
                embeddings = generate_embeddings(extracted_text)
                
                # Print embedding details BEFORE storing
                print(f"\n🔹 Generated Embeddings for '{os.path.basename(file_path)}' (Truncated):")
                print(f"{embeddings[:5]}... (Length: {len(embeddings)})")  # Print only first 5 values for readability

                metadata = {
                    "filename": os.path.basename(file_path),
                    "content": extracted_text
                }
                
                # Store in Qdrant
                store_embeddings([embeddings], [metadata])
                
                success_results.append({
                    "file": os.path.basename(file_path),
                    "content": extracted_text,
                    "status": "Successfully stored in Qdrant"
                })
                
                logging.info(f"--- Parsed and Stored Content for {os.path.basename(file_path)} ---")
                logging.info(extracted_text)

        except Exception as e:
            failed_results.append({
                "file": os.path.basename(file_path),
                "error": f"Processing failed: {e}"
            })
            logging.error(f"--- Failed to process content for {os.path.basename(file_path)} ---")
            logging.error(f"Error: {e}")


    return {
        "success": success_results,
        "failed": failed_results
    }
