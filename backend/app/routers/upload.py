from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.pdf_parser import extract_text_from_pdf

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read and process the PDF
    content = await file.read()
    extracted_text = extract_text_from_pdf(content)

    return {"filename": file.filename, "content": extracted_text[:500]}  # Return preview of extracted text