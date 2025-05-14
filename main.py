import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# Import routers
from routes import admin_route,asta_route

app = FastAPI()

app.mount("/static",StaticFiles(directory="static"),name = "static-directory")

# For templates
# templates = Jinja2Templates(directory="templates")

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

# Run the application with: uvicorn main:app --reload
if __name__ == "__main__":
    
    uvicorn.run("main:app", host="localhost", port=5451, reload=True)