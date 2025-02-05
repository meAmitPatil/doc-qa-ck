from fastapi import APIRouter, UploadFile, File, HTTPException
import os

router = APIRouter()

# Path to save uploaded files
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    uploaded_file_names = []

    # Process each file
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        uploaded_file_names.append(file.filename)

    return {"uploaded_files": uploaded_file_names}
