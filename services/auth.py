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

    def create_access_token(self, user: User, exp) -> str:
            """
            Creates a new JWT access token for a given user.
            """
            if not exp:
                expires_delta = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            else:
                expires_delta = exp
            expire = datetime.utcnow() + expires_delta
            
            # Data to be encoded in the token's payload
            to_encode = {
                "username": user.username,
                "role": user.role,
                "display_name": user.display_name,
                "exp": expire
            }
            
            encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
            return encoded_jwt

    def decode_access_token(self, token: str) -> Optional[Dict]:
        """
        Decodes a JWT token, validates its signature, and checks if the user
        it belongs to still exists and is active in the database.
        Returns the payload if valid, otherwise None.
        """
        try:
            # First, decode the token to check its signature and expiration
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("username")
            if username is None:
                # Token is malformed if it lacks a username
                return None
        except JWTError:
            # Token is invalid (bad signature, expired, etc.)
            return None

        try:
            user = self.user_service.get_user_by_username(username=username)
            # Also check if the user account has been disabled since the token was issued
            if user.disabled:
                return None
        except HTTPException as e:
            # If the UserService raises a 404, the user does not exist.
            if e.status_code == status.HTTP_404_NOT_FOUND:
                return None
            # Re-raise any other unexpected HTTP exceptions
            raise e
        
        # If all checks pass, the token is valid for an existing, active user.
        return payload