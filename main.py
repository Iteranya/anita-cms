# file: main.py

import os
import sys
import shutil
import secrets
import glob
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Request, Depends, status # Added status for clarity
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# --- CSRF Protection Integration ---
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
# --- FIX: Changed from pydantic_settings.BaseSettings to pydantic.BaseModel ---
from pydantic import BaseModel # Use BaseModel for simple data validation, not BaseSettings for auto-env loading

# --- Configuration & Environment Loading ---
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
load_dotenv(ENV_PATH)

# Add base directory to sys.path for module discovery (e.g., 'src')
sys.path.append(str(BASE_DIR))

# Import database (after path setup)
from data import database
# --- Using the renamed dependency function as discussed ---
from src.dependencies import csrf_protect_post_put_delete 

# Import all route modules
from routes import (
    admin_route,
    aina_route,
    asta_route,
    auth_route,
    file_route,
    collections_route,
    media_route,
    pages_route, 
    public_route,
    roles_route,
    config_route,
    dashboard_route
)

# --- CSRF Settings Model ---
# --- FIX: Changed from BaseSettings to BaseModel and removed Config class ---
class CsrfSettings(BaseModel):
    """
    Pydantic model for CSRF settings. Using BaseModel instead of BaseSettings
    prevents it from automatically trying to load all environment variables,
    which was causing the "extra inputs not permitted" validation error previously.
    """
    secret_key: str
    httponly:bool

# --- Interactive Setup Helper ---
def interactive_setup():
    """
    Handles initial setup:
    1. Selects a database template (Theme) if anita.db is missing.
    2. Generates JWT_SECRET and CSRF_SECRET if missing from .env.
    """
    
    db_path = BASE_DIR / "anita.db"
    templates_dir = BASE_DIR / "anita-template"

    if not db_path.exists():
        print("\n⚠️  No database found (anita.db).")
        
        if not templates_dir.exists():
            os.makedirs(templates_dir)
            
        available_templates = list(templates_dir.glob("*.db"))
        
        if not available_templates:
            print("❌ No database templates found in /anita-template folder!")
            print("Please place your template .db files there and restart.")
            sys.exit(1)
        print("🏗️  Welcome to Anita CMS Setup!")
        print("   We need to initialize your database.")
        print("   Since this is a new installation, please select a Starter Template.")
        print("   (This will configure your initial pages, roles, and settings)")

        print("\n📂 Available Starter Templates:")
        for idx, temp in enumerate(available_templates, 1):
            print(f"   [{idx}] {temp.name}")

        selected_index = -1
        while selected_index < 0 or selected_index >= len(available_templates):
            try:
                choice = input("\nEnter the number of your choice: ")
                selected_index = int(choice) - 1
            except ValueError:
                pass

        selected_template = available_templates[selected_index]
        print(f"🔄 Copying '{selected_template.name}' to 'anita.db'...")
        shutil.copy(selected_template, db_path)
        print("✅ Database initialized successfully.\n")
    
    # 2. Secret Generation (JWT & CSRF)
    # Reload env in case it was created/modified externally since script start
    load_dotenv(ENV_PATH, override=True)
    
    secrets_to_check = {
        "JWT_SECRET": "JSON Web Token authentication",
        "CSRF_SECRET": "Cross-Site Request Forgery protection"
    }

    for secret_name, purpose in secrets_to_check.items():
        if not os.getenv(secret_name):
            print(f"🔑 {secret_name} for {purpose} not found in .env.")
            gen_choice = input("Generate a secure random secret now? [Y/n]: ").strip().lower()

            if gen_choice in ["", "y", "yes", "Y"]:
                secret_value = secrets.token_hex(32)
                
                content = ""
                if ENV_PATH.exists():
                    with open(ENV_PATH, "r") as f:
                        content = f.read()
                
                prefix = "\n" if content and not content.endswith("\n") else ""
                with open(ENV_PATH, "a") as f:
                    f.write(f"{prefix}{secret_name}={secret_value}\n")
                
                print(f"✅ Generated new {secret_name} and saved to .env.")
                # Reload environment to apply the change immediately
                load_dotenv(ENV_PATH, override=True) 
            else:
                print(f"❌ Cannot proceed without {secret_name}. Exiting.")
                sys.exit(1)

# --- Database Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application starting up...")
    database.Base.metadata.create_all(bind=database.engine)
    yield
    print("👋 Application shutting down...")


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Anita CMS",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=True
)

# --- CSRF Exception Handler ---
@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# --- Load CSRF settings ---
@CsrfProtect.load_config
def get_csrf_config():
    secret = os.getenv("CSRF_SECRET")
    
    if not secret:
        raise ValueError("CSRF_SECRET environment variable not set. Please run setup or add it to .env.")

    return CsrfSettings(
        secret_key=secret,
        httponly=False
    )

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5469"],
    allow_credentials=True, 
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)

# --- Static Files ---
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static-directory")
app.mount("/uploads", StaticFiles(directory=BASE_DIR / "uploads"), name="uploads-directory")

# --- API Router Organization ---
api_router = APIRouter()

# 1. ROUTERS THAT REQUIRE SITE-WIDE CSRF PROTECTION
# These routers will have csrf_protect_post_put_delete applied to ALL their endpoints
# (except for GET/HEAD/OPTIONS, which are implicitly skipped by the dependency's internal logic)
protected_routers = [
    admin_route.router,
    config_route.router,
    aina_route.router,
    asta_route.router,
    collections_route.router,
    file_route.router,
    roles_route.router,
    pages_route.router, 
]

# --- FIX: This is the crucial change. Apply dependencies using include_router's 'dependencies' argument ---
for router in protected_routers:
    api_router.include_router(
        router,
        dependencies=[Depends(csrf_protect_post_put_delete)] 
    )

# 2. ROUTERS THAT ARE EXEMPT FROM GLOBAL CSRF PROTECTION or HANDLE IT INTERNALLY
# These routers are included WITHOUT the global CSRF dependency.
# 'auth_route.router' is here because its GET endpoints must be accessible to set the cookie,
# and its POST endpoints are protected individually within routes/auth_route.py.
api_router.include_router(auth_route.router)
api_router.include_router(dashboard_route.router)
api_router.include_router(media_route.router)
api_router.include_router(public_route.router)
# Add the main API router to the FastAPI app
app.include_router(api_router)

# --- Main Entry Point ---
if __name__ == "__main__":
    interactive_setup()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5469
    print(f"Starting server on http://127.0.0.1:{port}")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)