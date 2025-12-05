import time
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from src.auth import get_current_user
from PIL import Image
import io
from typing import List

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
        
        # Create a list of dictionaries containing both the ID (filename) and the Display URL
        images = []
        for f in files:
            if f.lower().endswith(image_extensions):
                images.append({
                    "filename": f,              # Use this for DELETE requests
                    "url": f"/media/{f}"        # Use this for Markdown/HTML display
                })
                
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
async def upload_media(
    files: List[UploadFile] = File(...),
    user: dict = Depends(get_current_user)
):
    uploaded_files = []
    
    for file in files:
        try:
            contents = await file.read()
            if not contents:
                raise ValueError("No data read from file")
            
            image = Image.open(io.BytesIO(contents))
            original_format = image.format
            
            # Handle transparency
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            original_name = os.path.splitext(file.filename)[0]
            timestamp = int(time.time())
            
            # Compression logic
            compressed_files = []
            
            # Strategy 1: JPEG
            if original_format in ['JPEG', 'JPG']:
                jpg_path = os.path.join(MEDIA_DIR, f"{original_name}_{timestamp}_temp.jpg")
                image.save(jpg_path, 'JPEG', quality=75, optimize=True)
                compressed_files.append(('jpg', jpg_path, os.path.getsize(jpg_path)))
            
            # Strategy 2: WebP
            webp_path = os.path.join(MEDIA_DIR, f"{original_name}_{timestamp}_temp.webp")
            webp_quality = 75 if original_format in ['JPEG', 'JPG'] else 85
            image.save(webp_path, 'WEBP', quality=webp_quality, method=4)
            compressed_files.append(('webp', webp_path, os.path.getsize(webp_path)))
            
            # Pick best
            best_format, best_path, best_size = min(compressed_files, key=lambda x: x[2])
            
            # Rename
            final_filename = f"{original_name}_{timestamp}.{best_format}"
            final_path = os.path.join(MEDIA_DIR, final_filename)
            os.rename(best_path, final_path)
            
            # Cleanup
            for fmt, path, _ in compressed_files:
                if path != best_path and os.path.exists(path):
                    os.remove(path)
            
            uploaded_files.append({
                "original": file.filename,
                "saved_as": final_filename,
                "url": f"/media/{final_filename}",  # <--- ADDED THIS RELATIVE URL
                "size": best_size,
                "format_chosen": best_format
            })
            
        except Exception as e:
            print(f"Error processing {file.filename}: {str(e)}")
            uploaded_files.append({
                "original": file.filename,
                "error": str(e)
            })
    
    return {
        "status": "success",
        "total": len(files),
        "files": uploaded_files
    }

@router.delete("/{filename}")
async def delete_media(filename: str, user: dict = Depends(get_current_user)):
    if any(sep in filename for sep in ("..", "/", "\\")):
        raise HTTPException(status_code=400, detail="Invalid filename")
    file_path = os.path.join(MEDIA_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"status": "deleted", "filename": filename}