import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt  
from fastapi import HTTPException, status
from services.users import UserService, verify_password
from data.schemas import User 

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.SECRET_KEY = os.getenv("JWT_SECRET")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 300

        if not self.SECRET_KEY:
            raise ValueError("JWT_SECRET environment variable not set in .env file")

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticates a user by checking credentials against the database.
        """
        try:
            user = self.user_service.get_user_by_username(username)
        except HTTPException as e:
            if e.status_code == 404:
                return None 
            raise e

        if not verify_password(password, user.hashed_password):
            return None 

        if user.disabled:
            return None 

        # Pydantic v2 uses model_validate instead of from_orm
        return User.model_validate(user)

    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a new JWT access token using PyJWT.
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # PyJWT handles datetime serialization automatically in the 'exp' claim
        to_encode = {
            "username": user.username,
            "role": user.role,
            "display_name": user.display_name,
            "exp": expire
        }
        
        # PyJWT encode returns a string (in v2+), whereas Jose returned bytes sometimes depending on version
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodes a JWT token using PyJWT logic.
        """
        try:
            # SECURITY: Always pass algorithms as a list to prevent confusion attacks
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
            username: str = payload.get("username")
            if username is None:
                return None
                
        except jwt.ExpiredSignatureError:
            # Specific exception for expired tokens
            return None
        except jwt.InvalidTokenError:
            # Catch-all for other JWT errors (malformed, bad signature, etc)
            return None

        # Double-check DB (Stateful check for immediate banning)
        try:
            user = self.user_service.get_user_by_username(username=username)
            if user.disabled:
                return None
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                return None
            raise e
        
        return payload