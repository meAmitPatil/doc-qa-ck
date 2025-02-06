from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from app.utils.pdf_parser import extract_text_from_pdf  # Import the updated parser

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

    # Parse the uploaded files using pdf_parser
    parsed_results = []

    for file_path in uploaded_file_paths:
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
                extracted_text = extract_text_from_pdf(pdf_bytes)
                parsed_results.append({"file": os.path.basename(file_path), "content": extracted_text})
                print(f"--- Parsed Content for {os.path.basename(file_path)} ---")
                print(extracted_text)
        except Exception as e:
            parsed_results.append({"file": os.path.basename(file_path), "error": f"Parsing failed: {e}"})
            print(f"--- Failed to parse content for {os.path.basename(file_path)} ---")

    return {"parsed_results": parsed_results}
