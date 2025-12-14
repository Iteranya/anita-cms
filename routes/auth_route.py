import os
from fastapi import APIRouter, HTTPException, status, Response, Form, Depends
from fastapi.responses import FileResponse, RedirectResponse
from datetime import timedelta
from sqlalchemy.orm import Session

# --- New Imports for Service-Oriented Architecture ---
# Assumes a 'database.py' file with a get_db dependency provider
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

# --- ROUTES ---

@router.get("/login")
async def serve_login_page(user_service: UserService = Depends(get_user_service)):
    # If no users exist, force them to setup
    if not is_system_initialized(user_service):
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)
    
    return FileResponse("static/auth/login.html")

@router.post("/login")
async def login_for_access_token(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    auth_service: AuthService = Depends(get_auth_service)
):
    # 1. Authenticate using the AuthService
    user = auth_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # 2. Define Expiry based on "Remember Me"
    # The default expiry is handled within the AuthService, so we only need to
    # provide a value if we want to override it.
    expires_in = timedelta(days=7) if remember_me else None
    
    # 3. Create Token using the AuthService
    # The service now takes the Pydantic User model directly
    access_token = auth_service.create_access_token(
        user=user, 
        exp=expires_in
    )

    # Calculate max_age for the cookie
    if expires_in:
        max_age = int(expires_in.total_seconds())
    else:
        # Use the default from the auth service
        max_age = auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # 4. Set Secure Cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production(), 
        samesite="lax",
        max_age=max_age,
    )
    
    return {"status": "success", "role": user.role}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "success"}

@router.get("/setup")
async def serve_setup_page(user_service: UserService = Depends(get_user_service)):
    # If no users exist, force them to setup
    if is_system_initialized(user_service):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return FileResponse("static/auth/setup.html")

@router.post("/setup")
async def setup_admin_account(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    user_service: UserService = Depends(get_user_service)
):
    # Security: Double-check prevents overwriting if multiple people hit the endpoint
    if is_system_initialized(user_service):
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

    # Create the first user (Admin) using the UserService
    # The service handles password hashing and validation.
    print("Making admin creds")
    admin_user_data = schemas.UserCreateWithPassword(
        username=username,
        password=password,
        role="admin", 
        display_name="System Admin",
        # other fields can have defaults in the Pydantic model
    )
    
    # The create_user method in the service will handle potential
    # username conflicts and other business logic.
    user_service.create_user(admin_user_data)
    
    return {
        "status": "success",
        "message": "Admin account created successfully. You may now login."
    }

@router.get("/check-setup")
async def check_setup(user_service: UserService = Depends(get_user_service)):
    """
    Client-side helper to check if the app needs to run the setup flow.
    """
    return {
        "initialized": is_system_initialized(user_service)
    }

@router.get("/register")
async def serve_register_page(user_service: UserService = Depends(get_user_service)):
    # If no users exist, force them to setup
    if not is_system_initialized(user_service):
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)
    
    return FileResponse("static/auth/register.html")

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    display_name: str = Form(None), # Optional
    user_service: UserService = Depends(get_user_service)
):
    """
    Public endpoint to register a new account. 
    The role is strictly enforced as 'user'.
    """
    # 1. Input Validation
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

    # 2. Prepare Data
    new_user_data = schemas.UserCreateWithPassword(
        username=username,
        password=password,
        role="viewer", 
        display_name=display_name or username
    )

    # 3. Call Service
    # The service handles hashing and username uniqueness checks
    try:
        created_user = user_service.create_user(new_user_data)
    except HTTPException as e:
        # Pass through service-level exceptions (like Username taken)
        raise e

    return {
        "status": "success",
        "message": "User registered successfully",
        "username": created_user.username
    }