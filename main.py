from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from data import db
import uvicorn
from src.auth import Depends,get_current_user
# Import routers
from routes import admin_route,asta_route,media_route,aina_route,public_route,auth_route,mail_route

app = FastAPI()
db.get_connection()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static-directory")

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
app.include_router(public_route.router)
app.include_router(auth_route.router)
app.include_router(mail_route.router)

# Protected Routers
app.include_router(
    admin_route.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    asta_route.router,
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    aina_route.router,
    dependencies=[Depends(get_current_user)]
)


# Run the application with: uvicorn main:app --reload
if __name__ == "__main__":
    
    uvicorn.run("main:app", host="127.0.0.1", port=5468) 