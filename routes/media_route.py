from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from src.auth import get_current_user

router = APIRouter(prefix="/media", tags=["Media"])

MEDIA_DIR = "data/media"

# Make sure the media directory exists
os.makedirs(MEDIA_DIR, exist_ok=True)

@router.get("/")
async def list_images():
    try:
        # List all files in MEDIA_DIR
        files = os.listdir(MEDIA_DIR)
        # Filter only image files
        image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        images = [f for f in files if f.lower().endswith(image_extensions)]
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{filename}")
async def get_media(filename: str):
    # Prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = os.path.join(MEDIA_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path)


@router.post("/")
async def upload_media(file: UploadFile = File(...),user: dict = Depends(get_current_user)):
    file_path = os.path.join(MEDIA_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}

@router.delete("/{filename}")
async def delete_media(filename: str, user: dict = Depends(get_current_user)):
    if any(sep in filename for sep in ("..", "/", "\\")):
        raise HTTPException(status_code=400, detail="Invalid filename")
    file_path = os.path.join(MEDIA_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"status": "deleted", "filename": filename}