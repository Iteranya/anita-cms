from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from datetime import timedelta
from src.auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    secrets_file_exists,
    set_admin_password
)
from pydantic import BaseModel

router = APIRouter(prefix="/auth",tags=["Auth"])

class LoginForm(BaseModel):
    username: str
    password: str
    remember_me: bool = False

@router.get("/login")
async def serve_custom_page():
    if not secrets_file_exists():
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)
    return FileResponse("static/auth/login.html")

@router.post("/login")
async def login_for_access_token(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
):
    if not secrets_file_exists():
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)
    if not authenticate_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    expires_in = timedelta(days=7) if remember_me else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=expires_in
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Enable in production with HTTPS
        samesite="lax",
        max_age=expires_in.total_seconds(),
    )
    
    return {"status": "success"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "success"}

class SetupForm(BaseModel):
    username: str
    password: str
    confirm_password: str

@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    if secrets_file_exists():
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    return FileResponse("static/auth/setup.html")

@router.post("/setup")
async def setup_admin_account(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if secrets_file_exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin account already exists"
        )
    
    if password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    set_admin_password(password,username)
    
    return {
        "status": "success",
        "message": "Admin account created successfully"
    }

@router.get("/check-setup")
async def check_setup():
    return {
        "initialized": secrets_file_exists()
    }

