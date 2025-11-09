from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil

router = APIRouter(prefix="/ai", tags=["AI"])
