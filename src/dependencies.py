# file: auth/dependencies.py

from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from pydantic import ValidationError # <-- ADDED: For catching schema validation errors

from services.auth import AuthService
from services.users import UserService
from data.database import get_db
from data import schemas # <-- ADDED: Import your schemas module

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService with a DB session."""
    user_service = UserService(db)
    return AuthService(user_service)

def get_current_user(
    access_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> schemas.CurrentUser: # <--- CHANGED: Return type is now the Pydantic schema
    """
    FastAPI dependency to get the current authenticated user from a cookie.
    Returns a Pydantic model of the user's token data.
    Raises 401 Unauthorized if the user is not authenticated or the token is invalid.
    """
    if not access_token:
        return None
    
    payload = auth_service.decode_access_token(access_token)
    if not payload:
        return None
    
    try:
        # CHANGED: Convert the dictionary payload into your Pydantic model
        # This provides validation and enables attribute access (e.g., user.username)
        return schemas.CurrentUser(**payload)
    except ValidationError:
        # Catches cases where the token is valid but the payload is malformed
        return None

def require_permission(permission: str):
    """
    A flexible dependency generator that requires a specific permission.
    Example Usage: `user: schemas.CurrentUser = Depends(require_permission("page:create"))`
    """
    def dependency(
        # CHANGED: The dependency now expects and returns the Pydantic schema
        current_user: schemas.CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> schemas.CurrentUser:
        user_service = UserService(db)
        user_role = current_user.role
        
        all_roles = user_service.get_all_roles()
        user_permissions = all_roles.get(user_role, [])
        
        # Admin role with wildcard has all permissions
        if "*" in user_permissions:
            return current_user
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required."
            )
        return current_user
    return dependency

# Specific permission dependencies now work seamlessly with the changes
require_admin = require_permission("*") 
require_editor = require_permission("page:update")

def optional_user(
    access_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[schemas.CurrentUser]: # <--- CHANGED: Return type is now the optional Pydantic schema
    """
    FastAPI dependency that provides the user model if authenticated,
    but does not raise an error if not. Returns None for anonymous users
    or if the token is invalid.
    """
    if not access_token:
        return None
    
    payload = auth_service.decode_access_token(access_token)
    if not payload:
        return None
        
    try:
        # CHANGED: Also convert to the Pydantic model here
        return schemas.CurrentUser(**payload)
    except ValidationError:
        # If the token exists but is malformed, treat as an anonymous user
        return None