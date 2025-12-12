from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from src.dependencies import get_current_user

router = APIRouter(prefix="/file", tags=["File"])

FILE_DIR = "uploads/file"

# Make sure the media directory exists
os.makedirs(FILE_DIR, exist_ok=True)

@router.get("/{filename}", response_class=FileResponse)
async def get_file(filename: str):
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path)

@router.post("/")
async def upload_file(file: UploadFile = File(...),user: dict = Depends(get_current_user)):
    file_path = os.path.join(FILE_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}

@router.delete("/{filename}")
async def delete_file(filename: str, user: dict = Depends(get_current_user)):
    if any(sep in filename for sep in ("..", "/", "\\")):
        raise HTTPException(status_code=400, detail="Invalid filename")
    file_path = os.path.join(FILE_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"status": "deleted", "filename": filename}