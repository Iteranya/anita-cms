# file: api/media.py

from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from pytest import Session
from data.database import get_db
from services.users import UserService
from src.dependencies import get_current_user

from services.media import CopypartyError, MediaService, InvalidFileNameError, FileNotFoundError, ImageProcessingError
from data.schemas import MediaFile, UploadResult, UploadedFileReport,CurrentUser

router = APIRouter(prefix="/media", tags=["Media"])
media_service = MediaService() # Instantiate the service once

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get an instance of UserService with a DB session."""
    return UserService(db)

@router.get("/", response_model=List[MediaFile])
async def list_images(
    user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),  
):
    """List all available media files."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_list_media = "*" in user_permissions or "media:read" in user_permissions
    
    if not can_list_media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    images = media_service.list_files()
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
    user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),  
):
    """Upload one or more image files for processing and storage."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_create_media = "*" in user_permissions or "media:create" in user_permissions

    if not can_create_media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    

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
    user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),  
):
    """Delete a media file."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_delete_media = "*" in user_permissions or "media:delete" in user_permissions

    if not can_delete_media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        media_service.delete_file(filename)
        return # Return nothing on success for 204
    except InvalidFileNameError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_media_to_remote(
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Trigger a synchronization of local files to the Copyparty server.
    This checks for files missing on the remote server and uploads them.
    """
    user_permissions = user_service.get_user_permissions(user.username)
    # Require admin or specific media permission
    can_sync = "*" in user_permissions or "media:update" in user_permissions

    if not can_sync:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Check if copyparty is enabled before running
    if not media_service.copyparty:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Copyparty integration is not configured.")

    try:
        # Since sync involves network IO and could take time, 
        # we can either await it (blocking response) or run it in background.
        # For small folders, awaiting is fine for immediate feedback.
        # For large folders, use background_tasks.add_task(media_service.sync_to_copyparty)
        
        # Here we wait for the result to return the report
        report = media_service.sync_to_copyparty()
        return report

    except CopypartyError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))