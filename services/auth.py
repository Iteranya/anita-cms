import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status
from jose import JWTError, jwt

# Import the user service to interact with user data
from services.users import UserService, verify_password, hash_password
from data.schemas import User  # Pydantic schema for the user

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.SECRET_KEY = os.getenv("JWT_SECRET")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        if not self.SECRET_KEY:
            raise ValueError("JWT_SECRET environment variable not set in .env file")

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticates a user by checking credentials against the database via UserService.
        Returns the Pydantic User model on success, otherwise None.
        """
        try:
            user = self.user_service.get_user_by_username(username)
        except HTTPException as e:
            if e.status_code == 404:
                return None # User not found
            raise e

        if not verify_password(password, user.hashed_password):
            return None # Invalid password

        if user.disabled:
            return None # Disabled user

        return User.from_orm(user) # Return Pydantic model

    def create_access_token(self, user: User) -> str:
        """
        Creates a new JWT access token for a given user.
        """
        expires_delta = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        # Data to be encoded in the token's payload
        to_encode = {
            "sub": user.username,
            "role": user.role,
            "display_name": user.display_name,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Optional[Dict]:
        """
        Decodes a JWT token and returns its payload if valid.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("sub") is None:
                return None
            return payload
        except JWTError:
            return None