import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import json
from pathlib import Path

from pydantic import BaseModel

# Security settings


SECRETS_FILE = "secret.json"
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-here")  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AdminUser(BaseModel):
    username: str
    password: str  # This will be hashed before storage
    disabled: bool = False

# Load user data
def get_user_data():
    try:
        with open("secret.json") as f:
            return json.load(f)["admin"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        raise RuntimeError("Invalid or missing secret.json file")

def verify_password(plain_password: str, hashed_password: str):
    print(f"Plain: {plain_password}\nHashed: {hashed_password}")
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    print(f"Username: {username}\nPassword: {password}" )
    user_data = get_user_data()
    if username != user_data["username"]:
        return False
    if not verify_password(password, user_data["hashed_password"]):
        return False
    return True

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def optional_auth(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_secrets_path() -> Path:
    return Path(SECRETS_FILE)

def secrets_file_exists() -> bool:
    return get_secrets_path().exists()

def create_default_secrets():
    secrets = {
        "admin": {
            "username": "admin",
            "hashed_password": "",  # Will be set during setup
            "disabled": False
        }
    }
    save_secrets(secrets)

def save_secrets(secrets: dict):
    with open(SECRETS_FILE, 'w') as f:
        json.dump(secrets, f, indent=2)

def get_admin_user() -> AdminUser:
    if not secrets_file_exists():
        raise HTTPException(
            status_code=400,
            detail="System not initialized. Please create admin account."
        )
    
    with open(SECRETS_FILE) as f:
        data = json.load(f)
        return AdminUser(**data["admin"])


# Ah, here,
def set_admin_password(password: str, username = "Admin"):
    hashed_password = pwd_context.hash(password)
    
    if secrets_file_exists():
        with open(SECRETS_FILE) as f:
            secrets = json.load(f)
    else:
        secrets = {
            "admin": {
                "username": username,
                "hashed_password": hashed_password,
                "disabled": False
            }
        }
    
    secrets["admin"]["hashed_password"] = hashed_password
    save_secrets(secrets)

