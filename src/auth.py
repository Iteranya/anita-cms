import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security settings
SECRETS_FILE = "secret.json"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# --- NEW MODEL STRUCTURE ---
class UserAccount(BaseModel):
    username: str
    password: Optional[str] = None # Used for input, not stored in JSON
    hashed_password: str
    role: str = "user"             # Default role
    display_name: str = "New User" # Default display name
    pfp_url: Optional[str] = None  # Profile picture URL
    disabled: bool = False

# --- FILE OPERATIONS ---

def get_secrets_path() -> Path:
    return Path(SECRETS_FILE)

def ensure_secrets_file():
    """Ensures the JSON file exists with a valid structure."""
    if not get_secrets_path().exists():
        with open(SECRETS_FILE, 'w') as f:
            json.dump({"users": {}}, f, indent=2)

def load_all_users() -> Dict:
    """Returns the dictionary of all users."""
    ensure_secrets_file()
    try:
        with open(SECRETS_FILE, "r") as f:
            data = json.load(f)
            return data.get("users", {})
    except (json.JSONDecodeError, KeyError):
        return {}

def save_user_data(username: str, user_data: dict):
    """Saves or updates a single user."""
    ensure_secrets_file()
    
    # Load existing full data
    with open(SECRETS_FILE, "r") as f:
        try:
            full_data = json.load(f)
        except json.JSONDecodeError:
            full_data = {"users": {}}

    if "users" not in full_data:
        full_data["users"] = {}

    # Update specific user
    full_data["users"][username] = user_data

    # Write back
    with open(SECRETS_FILE, "w") as f:
        json.dump(full_data, f, indent=2)

def get_user_by_username(username: str) -> Optional[dict]:
    users = load_all_users()
    return users.get(username)

# --- AUTH LOGIC ---

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user_dict = get_user_by_username(username)
    if not user_dict:
        return False
    
    if not verify_password(password, user_dict["hashed_password"]):
        return False
        
    if user_dict.get("disabled", False):
        return False
        
    return user_dict

def create_access_token(data: dict, expires_delta: timedelta = None):
    SECRET_KEY = os.getenv("JWT_SECRET") 
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- DEPENDENCIES ---

async def get_current_user(request: Request):
    SECRET_KEY = os.getenv("JWT_SECRET") 
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Validate that the token contains at least a username (sub)
        if payload.get("sub") is None:
            raise JWTError
        return payload 
        # Returns dict: {'sub': 'username', 'role': 'admin', 'display_name': '...', 'exp': ...}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_admin(payload: dict = Depends(get_current_user)):
    """Helper dependency to lock routes to admins only"""
    role = payload.get("role", "user")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return payload

async def optional_auth(request: Request):
    SECRET_KEY = os.getenv("JWT_SECRET") 
    if not SECRET_KEY:
        return None
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# --- USER MANAGEMENT FUNCTIONS ---

def create_or_update_user(
    username: str, 
    password: str = None, 
    role: str = "user", 
    display_name: str = None,
    pfp_url: str = None
):
    """
    Creates a new user or updates an existing one. 
    If password is None, it keeps the old password (for updates).
    """
    existing_user = get_user_by_username(username)
    
    # Determine Hash
    if password:
        final_hash = get_password_hash(password)
    elif existing_user:
        final_hash = existing_user["hashed_password"]
    else:
        raise ValueError("Cannot create new user without a password")

    # Set Defaults if not provided
    final_role = role if role else (existing_user["role"] if existing_user else "user")
    final_name = display_name if display_name else (existing_user.get("display_name", username) if existing_user else username)
    final_pfp = pfp_url if pfp_url else (existing_user.get("pfp_url") if existing_user else "")

    user_data = {
        "username": username,
        "hashed_password": final_hash,
        "role": final_role,
        "display_name": final_name,
        "pfp_url": final_pfp,
        "disabled": False
    }
    
    save_user_data(username, user_data)
    print(f"User '{username}' saved with role '{final_role}'.")

def create_default_admin():
    """Initializes the system with a default admin if no users exist."""
    users = load_all_users()
    if not users:
        print("No users found. Creating default 'admin' account.")
        # Pass a default password, usually you'd want to prompt for this or generate it
        create_or_update_user("admin", "admin123", role="admin", display_name="System Admin")