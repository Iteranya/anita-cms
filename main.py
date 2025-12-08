# main.py

import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# --- Configuration & Environment Loading ---
# Load environment variables from .env file
load_dotenv()

# We need to add the project root to the path to allow for clean imports
# Adjust this if your main.py is in a different location (e.g., inside an 'app' folder)
sys.path.append(str(Path(__file__).resolve().parent))

# Now that the path is set, we can use absolute imports
from data import crud, database
# Import all your route modules
from routes import (
    admin_route,
    aina_route,
    asta_route,
    auth_route,
    file_route,
    forms_route,
    media_route,
    pages_route, 
    public_route,
    roles_route,
    config_route
)

# --- Pre-startup Checks ---
if not os.getenv("JWT_SECRET"):
    print("❌ ERROR: JWT_SECRET not found in .env file!")
    print("Please add JWT_SECRET to your .env file before running the application.")
    sys.exit(1)


# --- Database Initialization & Seeding (using lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    print("🚀 Application starting up...")
    
    # Create database tables if they don't exist
    database.Base.metadata.create_all(bind=database.engine)
    
    # Get a database session to perform seeding
    db = database.SessionLocal()
    try:
        print("🌱 Seeding database if necessary...")
        # Call all your seeding functions. They are idempotent (safe to run multiple times).
        crud.seed_default_roles(db)
        crud.seed_default_pages(db)
        # Add any other seeding functions here
        print("✅ Seeding complete.")
    finally:
        db.close()
        
    yield # The application runs here

    # This code runs on shutdown
    print("👋 Application shutting down...")


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Your Project API",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=True
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files ---
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static-directory")
app.mount("/uploads", StaticFiles(directory=BASE_DIR / "uploads"), name="uploads-directory")

# --- API Router Organization ---

# This is the main router for your entire API, prefixed for versioning
api_router = APIRouter()

# This router is for all routes that REQUIRE authentication
# We apply the dependency here once, and it applies to all included routers.

# Include all protected routes into the protected_router
api_router.include_router(admin_route.router, tags=["Admin"])
api_router.include_router(config_route.router, tags=["Config"])
api_router.include_router(aina_route.router, tags=["Aina"])
api_router.include_router(asta_route.router, tags=["Asta"])
api_router.include_router(media_route.router, tags=["Media"])
api_router.include_router(forms_route.router, tags=["Forms"])
api_router.include_router(file_route.router, tags=["Files"])
api_router.include_router(roles_route.router, tags=["Roles"])
api_router.include_router(pages_route.router, tags=["Pages"]) 
api_router.include_router(auth_route.router, tags=["Authentication"]) 
api_router.include_router(public_route.router, tags=["Public"])   

# Finally, include the versioned API router in the main app
app.include_router(api_router)


# --- Main Entry Point for Uvicorn ---
if __name__ == "__main__":
    # Get port from command-line argument, default to 5469
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5469
    print(f"Starting server on http://127.0.0.1:{port}")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)