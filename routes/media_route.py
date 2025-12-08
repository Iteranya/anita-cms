# file: api/media.py

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse

# Adjust this import to your project's authentication location
from src.dependencies import get_current_user

from services.media import MediaService, InvalidFileNameError, FileNotFoundError, ImageProcessingError
from data.schemas import MediaFile, UploadResult, UploadedFileReport

router = APIRouter(prefix="/media", tags=["Media"])
media_service = MediaService() # Instantiate the service once

@router.get("/", response_model=List[MediaFile])
async def list_images():
    """List all available media files."""
    images = media_service.list_files()
    print(images)
    return images

@router.get("/{filename}")
async def get_media(filename: str):
    """Retrieve a single media file."""
    try:
        file_path = media_service.get_file_path(filename)
        return FileResponse(path=file_path)
    except InvalidFileNameError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/", response_model=UploadResult)
async def upload_media(
    files: List[UploadFile] = File(...),
    user: dict = Depends(get_current_user) # Authentication is an API-layer concern
):
    """Upload one or more image files for processing and storage."""
    reports: List[UploadedFileReport] = []
    for file in files:
        report_data = {"original": file.filename}
        try:
            contents = await file.read()
            if not contents:
                raise ValueError("Uploaded file is empty.")
            
            processed_data = media_service.process_and_save_image(contents, file.filename)
            report_data.update(processed_data)

        except (ImageProcessingError, ValueError) as e:
            report_data["error"] = str(e)
        except Exception as e:
            # Catch unexpected errors
            report_data["error"] = f"An unexpected error occurred: {e}"
        
        reports.append(UploadedFileReport(**report_data))
    
    return UploadResult(status="completed", total=len(files), files=reports)

@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    filename: str, 
    user: dict = Depends(get_current_user)
):
    """Delete a media file."""
    try:
        media_service.delete_file(filename)
        return # Return nothing on success for 204
    except InvalidFileNameError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))