import os
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from data import db, forms_db
from src.auth import Depends, get_current_user

# Load environment variables
load_dotenv()

# Import routers
from routes import (
    admin_route,
    aina_route,
    asta_route,
    auth_route,
    file_route,
    forms_route,
    mail_route,
    media_route,
    public_route,
)

# Check if JWT_SECRET exists
if not os.getenv("JWT_SECRET"):
    print("❌ ERROR: JWT_SECRET not found in .env file!")
    print("Please add JWT_SECRET to your .env file before running the application.")
    sys.exit(1)

app = FastAPI(redirect_slashes=True)
db.get_connection()
forms_db.get_connection()
BASE_DIR = Path(__file__).resolve().parent
app.mount(
    "/static", StaticFiles(directory=BASE_DIR / "static"), name="static-directory"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_route.router)
app.include_router(asta_route.router)
app.include_router(media_route.router)
app.include_router(aina_route.router)
app.include_router(auth_route.router)
app.include_router(mail_route.router)
app.include_router(forms_route.router)
app.include_router(file_route.router)
# Protected Routers
app.include_router(admin_route.router, dependencies=[Depends(get_current_user)])
app.include_router(asta_route.router, dependencies=[Depends(get_current_user)])
app.include_router(aina_route.router, dependencies=[Depends(get_current_user)])
app.include_router(public_route.router)

# Run the application with: uvicorn main:app --reload
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5469
    uvicorn.run("main:app", host="127.0.0.1", port=port)
