# file: auth.py

import os
from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv
from data import database

# Load environment variables
load_dotenv()

# Security settings remain the same
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# --- MODEL STRUCTURE (Unchanged) ---
class UserAccount(BaseModel):
    username: str
    password: Optional[str] = None # Used for input, not stored
    hashed_password: str
    role: str = "user"
    display_name: str = "New User"
    pfp_url: Optional[str] = None
    disabled: bool = False

# --- FILE OPERATIONS (REMOVED) ---
# All json file handling has been removed and replaced with database calls.

# --- UPDATED USER LOOKUP ---
def get_user_by_username(username: str) -> Optional[dict]:
    """Wrapper function that calls the database to get user data."""
    return database.get_user_by_username_db(username)

# --- AUTH LOGIC (Logic is unchanged, data source is now DB) ---

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticates a user against the database.
    Returns the user dictionary on success, otherwise False.
    """
    user_dict = get_user_by_username(username)
    if not user_dict:
        return None
    
    if not verify_password(password, user_dict["hashed_password"]):
        return None
        
    # The database stores disabled as 0 or 1
    if user_dict.get("disabled"): 
        return None
        
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

# --- DEPENDENCIES (Unchanged as they operate on the token, not storage) ---

async def get_current_user(request: Request) -> dict:
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

async def require_admin(payload: dict = Depends(get_current_user)) -> dict:
    """Helper dependency to lock routes to admins only"""
    role = payload.get("role", "user")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return payload

async def optional_auth(request: Request) -> Optional[dict]:
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

# --- REFACTORED USER MANAGEMENT FUNCTIONS ---

def create_or_update_user(
    username: str, 
    password: str = None, 
    role: str = None, 
    display_name: str = None,
    pfp_url: str = None
):
    """
    Creates a new user or updates an existing one by saving to the database.
    If password is None on an existing user, it keeps the old password.
    """
    existing_user = get_user_by_username(username)
    
    if password:
        final_hash = get_password_hash(password)
    elif existing_user:
        final_hash = existing_user["hashed_password"]
    else:
        raise ValueError("Cannot create a new user without a password")

    # Build the user data dictionary, falling back to existing data if available
    user_data = {
        "username": username,
        "hashed_password": final_hash,
        "role": role or (existing_user.get("role") if existing_user else "user"),
        "display_name": display_name or (existing_user.get("display_name", username) if existing_user else username),
        "pfp_url": pfp_url or (existing_user.get("pfp_url") if existing_user else None),
        "disabled": False
    }
    
    # Save to the database using the new function
    database.save_user_db(user_data)
    print(f"User '{username}' saved to database with role '{user_data['role']}'.")

def create_default_admin():
    """Initializes the system with a default admin if no users exist in the DB."""
    # Check the database instead of the file
    if database.count_users_db() == 0:
        print("No users found in database. Creating default 'admin' account.")
        create_or_update_user(
            username="admin", 
            password="admin123", # Consider making this more secure
            role="admin", 
            display_name="System Admin"
        )