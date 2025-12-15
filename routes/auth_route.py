import os
from fastapi import APIRouter, HTTPException, status, Response, Form, Depends
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from datetime import timedelta
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from data.database import get_db 
from data import schemas
from services.auth import AuthService
from services.users import UserService

# --- Dependency Setup ---
# These functions allow FastAPI to inject service instances into our routes.
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)

# --- Router Setup ---
router = APIRouter(prefix="/auth", tags=["Auth"])

# --- HELPERS ---

def is_system_initialized(user_service: UserService) -> bool:
    return len(user_service.get_all_users()) > 0

def is_production() -> bool:
    """Simple check to determine if we should enforce HTTPS only cookies."""
    return os.getenv("APP_ENV", "dev").lower() in ["prod", "production"]


@router.get("/login")
async def serve_login_page(
    response: Response,
    user_service: UserService = Depends(get_user_service)
):
    if not is_system_initialized(user_service):
        return RedirectResponse(url="/auth/setup", status_code=302)

    with open("static/auth/login.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    return HTMLResponse(content=html, headers=response.headers)


@router.post("/login")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    auth_service: AuthService = Depends(get_auth_service),
    csrf_protect: CsrfProtect = Depends() 
):
    user = auth_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    expires_in = timedelta(days=7) if remember_me else None
    
    access_token = auth_service.create_access_token(
        user=user, 
        exp=expires_in
    )

    max_age = int(expires_in.total_seconds()) if expires_in else auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Generate CSRF token BEFORE creating response
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    
    # Create response
    response = JSONResponse(content={
        "status": "success", 
        "role": user.role,
        "csrf_token": csrf_token  # Include in response body
    })
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production(), 
        samesite="lax",
        max_age=max_age,
    )
    
    # Set CSRF cookie with the signed token
    csrf_protect.set_csrf_cookie(signed_token, response)
    
    return response

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("csrf_token")
    response.delete_cookie("fastapi-csrf-token")
    response.delete_cookie("access_token")
    return {"status": "success"}

@router.get("/setup")
async def serve_setup_page(
    csrf_protect: CsrfProtect = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    if is_system_initialized(user_service):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    response = FileResponse("static/auth/setup.html")
    # Set the CSRF token cookie, arming the setup form
    csrf_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(response, csrf_token)
    return response

@router.post("/setup")
async def setup_admin_account(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    user_service: UserService = Depends(get_user_service),
    csrf_protect: CsrfProtect = Depends() # <--- FIX: Added CSRF dependency
):
    # FIX: Explicitly validate the token sent from the form
    await csrf_protect.validate_csrf()

    if is_system_initialized(user_service):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System is already initialized. Please login."
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

    admin_user_data = schemas.UserCreateWithPassword(
        username=username,
        password=password,
        role="admin", 
        display_name="System Admin",
    )
    
    user_service.create_user(admin_user_data)
    
    return {
        "status": "success",
        "message": "Admin account created successfully. You may now login."
    }

@router.get("/check-setup")
async def check_setup(user_service: UserService = Depends(get_user_service)):
    return {"initialized": is_system_initialized(user_service)}

@router.get("/register")
async def serve_register_page(
    csrf_protect: CsrfProtect = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    if not is_system_initialized(user_service):
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)
    
    response = FileResponse("static/auth/register.html")
    # Set the CSRF token cookie, arming the registration form
    csrf_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(response, csrf_token)
    return response

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    display_name: str = Form(None),
    user_service: UserService = Depends(get_user_service),
    csrf_protect: CsrfProtect = Depends() # <--- FIX: Added CSRF dependency
):
    # FIX: Explicitly validate the token sent from the form
    await csrf_protect.validate_csrf()

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

    new_user_data = schemas.UserCreateWithPassword(
        username=username,
        password=password,
        role="viewer", 
        display_name=display_name or username
    )

    try:
        created_user = user_service.create_user(new_user_data)
    except HTTPException as e:
        raise e

    return {
        "status": "success",
        "message": "User registered successfully",
        "username": created_user.username
    }