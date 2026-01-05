import os
from fastapi import APIRouter, HTTPException, Request, status, Response, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import timedelta
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session
from data.database import get_db 
from data import schemas
from services.auth import AuthService
from services.users import UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_auth_service(user_service: UserService = Depends(get_user_service)) -> AuthService:
    return AuthService(user_service)

# --- Router Setup ---
router = APIRouter(tags=["Auth"])

AUTH_DIR = "static/auth"
SPA_VIEWS = {"login", "setup", "register"}

# --- HELPERS ---

def is_system_initialized(user_service: UserService) -> bool:
    return len(user_service.get_all_users()) > 0

def is_production() -> bool:
    """Simple check to determine if we should enforce HTTPS only cookies."""
    return os.getenv("APP_ENV", "dev").lower() in ["prod", "production"]

def render_no_cache_html(file_path: str, is_partial: bool):
    """
    Reads file and adds headers to prevent caching issues between 
    partial (HTMX) and full (Browser) requests.
    """
    if not os.path.exists(file_path):
        return HTMLResponse("View not found", status_code=404)
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    response = HTMLResponse(content)
    response.headers["Vary"] = "HX-Request" 
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

# --- VIEWS (Read-Only Endpoints) ---

@router.get("/auth", include_in_schema=False)
async def serve_auth_page(user_service: UserService = Depends(get_user_service)):
    if not is_system_initialized(user_service):
        return RedirectResponse(url="/auth/setup", status_code=status.HTTP_302_FOUND)
    
    return RedirectResponse("/auth/login")

# --- CORRECTED auth_router FUNCTION ---
@router.get("/auth/{slug}", response_class=HTMLResponse)
async def auth_router(
    slug: str, 
    request: Request,
    csrf_protect: CsrfProtect = Depends()
):
    if slug not in SPA_VIEWS:
        raise HTTPException(status_code=404, detail="Page not found")

    if request.headers.get("HX-Request"):
        view_path = os.path.join(AUTH_DIR, "views", f"{slug}.html")
        response = render_no_cache_html(view_path, True)
    else:
        shell_path = os.path.join(AUTH_DIR, "index.html")
        response = render_no_cache_html(shell_path, False)

    # 1. Generate the tokens. This is a SYNCHRONOUS call. NO await.
    raw_token, signed_token = csrf_protect.generate_csrf_tokens()

    # 2. Set the cookie using the signed token. This is also SYNCHRONOUS. NO await.
    csrf_protect.set_csrf_cookie(signed_token, response)

    # 3. (Still correct and important!) Send the raw_token to the client
    #    so it can be used in subsequent request headers.
    response.headers["X-CSRF-Token"] = raw_token
    return response

@router.get("/auth/check-setup")
async def check_setup(user_service: UserService = Depends(get_user_service)):
    return {"initialized": is_system_initialized(user_service)}

# --- ACTIONS (State-Changing Endpoints, All CSRF Protected) ---

@router.post("/auth/login")
async def login_for_access_token(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    auth_service: AuthService = Depends(get_auth_service)
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
        expires_delta=expires_in
    )

    max_age = int(expires_in.total_seconds()) if expires_in else (auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production(), 
        samesite="lax",
        max_age=max_age,
    )
    
    return {"status": "success", "role": user.role}

@router.post("/auth/logout")
async def logout(
    response: Response,
    csrf_protect: CsrfProtect = Depends()
):
    response.delete_cookie("access_token")
    await csrf_protect.unset_csrf_cookie(response)
    return {"status": "success"}

@router.post("/auth/setup")
async def setup_admin_account(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    user_service: UserService = Depends(get_user_service)
):
    if is_system_initialized(user_service):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System is already initialized. Please login."
        )
    
    if password != confirm_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Passwords do not match")
    
    if len(password) < 8:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password must be at least 8 characters")

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

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    display_name: str = Form(None),
    user_service: UserService = Depends(get_user_service)
):
    if password != confirm_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Passwords do not match")

    if len(password) < 8:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password must be at least 8 characters")

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