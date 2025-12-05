import os
from fastapi import APIRouter, HTTPException, status, Response, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from datetime import timedelta
from pydantic import BaseModel
from typing import Optional

# Import the updated functions from your src.auth file
from src.auth import (
    authenticate_user,
    create_access_token,
    create_or_update_user,
    load_all_users,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- HELPERS ---

def is_system_initialized() -> bool:
    """Checks if at least one user exists in the system."""
    users = load_all_users()
    return len(users) > 0

def is_production() -> bool:
    """Simple check to determine if we should enforce HTTPS only cookies."""
    # check if 'MODE' env var is set to 'PROD' or similar
    return os.getenv("APP_ENV", "dev").lower() in ["prod", "production"]

# --- ROUTES ---

@router.get("/login")
async def serve_login_page():
    # If no users exist, force them to setup
    if not is_system_initialized():
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)
    
    return FileResponse("static/auth/login.html")

@router.post("/login")
async def login_for_access_token(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
):
    # Security: Don't allow login if system isn't set up (prevents weird states)
    if not is_system_initialized():
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)

    # 1. Authenticate (Returns full user dict or False)
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # 2. Define Expiry
    expires_in = timedelta(days=7) if remember_me else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 3. Create Token Payload (Includes Role & Display Name now!)
    token_payload = {
        "sub": user["username"],
        "role": user["role"],
        "display_name": user.get("display_name", user["username"]),
        "pfp_url": user.get("pfp_url", "")
    }

    access_token = create_access_token(
        data=token_payload, 
        expires_delta=expires_in
    )

    # 4. Set Secure Cookie
    # 'secure=True' requires HTTPS. We check environment to prevent localhost issues.
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # JavaScript cannot access this cookie (XSS protection)
        secure=is_production(), 
        samesite="lax", # CSRF protection
        max_age=int(expires_in.total_seconds()),
    )
    
    return {"status": "success", "role": user["role"]}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "success"}

# --- SETUP ROUTES ---

@router.get("/setup", response_class=HTMLResponse)
async def setup_page():
    # Security: Block setup page if an admin already exists
    if is_system_initialized():
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    return FileResponse("static/auth/setup.html")

@router.post("/setup")
async def setup_admin_account(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    # Security: Double check prevents overwriting if multiple people hit endpoint at once
    if is_system_initialized():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System is already initialized. Please login."
        )
    
    # Input Validation
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

    # Create the First User (Admin)
    # We set role='admin' specifically here
    create_or_update_user(
        username=username, 
        password=password, 
        role="admin", 
        display_name="System Admin",
        pfp_url="" 
    )
    
    return {
        "status": "success",
        "message": "Admin account created successfully. You may now login."
    }

@router.get("/check-setup")
async def check_setup():
    return {
        "initialized": is_system_initialized()
    }