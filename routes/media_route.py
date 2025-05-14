from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil

router = APIRouter(prefix="/media", tags=["Media"])

MEDIA_DIR = "data/media"

# Make sure the media directory exists
os.makedirs(MEDIA_DIR, exist_ok=True)

@router.get("/{filename}", response_class=FileResponse)
async def get_media(filename: str):
    file_path = os.path.join(MEDIA_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path)

@router.post("/")
async def upload_media(file: UploadFile = File(...)):
    file_path = os.path.join(MEDIA_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}
