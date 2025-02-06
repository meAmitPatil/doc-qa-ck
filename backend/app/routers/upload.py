from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from app.utils.pdf_parser import extract_text_from_pdf  # Import the parser
from app.utils.embeddings import generate_embeddings  # Import the embeddings
from app.utils.qdrant_client import store_embeddings  # Import the Qdrant storage function

router = APIRouter()

# Path to save uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    uploaded_file_paths = []

    # Save the uploaded files
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        uploaded_file_paths.append(file_path)

    # Parse the uploaded files, generate embeddings, and store in Qdrant
    parsed_results = []

    for file_path in uploaded_file_paths:
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
                extracted_text = extract_text_from_pdf(pdf_bytes)
                
                if not extracted_text.strip():
                    raise ValueError("No text extracted from the PDF. It may be scanned or corrupted.")
                
                # Generate embeddings for the extracted text
                embeddings = generate_embeddings(extracted_text)
                
                # Store embeddings in Qdrant
                metadata = {"filename": os.path.basename(file_path)}  # Add any additional metadata if required
                store_embeddings([embeddings], [metadata])
                
                parsed_results.append({
                    "file": os.path.basename(file_path),
                    "content": extracted_text,
                    "status": "Successfully stored in Qdrant"
                })
                
                print(f"--- Parsed and Stored Content for {os.path.basename(file_path)} ---")
                print(extracted_text)
        except Exception as e:
            parsed_results.append({
                "file": os.path.basename(file_path),
                "error": f"Processing failed: {e}"
            })
            print(f"--- Failed to process content for {os.path.basename(file_path)} ---")
            print(f"Error: {e}")

    return {"parsed_results": parsed_results}
