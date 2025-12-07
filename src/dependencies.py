# file: auth/dependencies.py

from typing import Optional, Dict
from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.orm import Session

from services.auth import AuthService
from services.users import UserService
from data.database import get_db

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService with a DB session."""
    user_service = UserService(db)
    return AuthService(user_service)

def get_current_user(
    access_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    """
    FastAPI dependency to get the current authenticated user from a cookie.
    Raises 401 Unauthorized if the user is not authenticated or the token is invalid.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = auth_service.decode_access_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return payload

def require_permission(permission: str):
    """
    A flexible dependency generator that requires a specific permission.
    Example Usage: `user: dict = Depends(require_permission("page:create"))`
    """
    def dependency(
        payload: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> dict:
        user_service = UserService(db)
        user_role = payload.get("role", "viewer")
        
        all_roles = user_service.get_all_roles()
        user_permissions = all_roles.get(user_role, [])
        
        # Admin role with wildcard has all permissions
        if "*" in user_permissions:
            return payload
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required."
            )
        return payload
    return dependency

# Specific permission dependencies for convenience
require_admin = require_permission("*") 
require_editor = require_permission("page:update")

def optional_user(
    access_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[Dict]:
    """
    FastAPI dependency that provides the user payload if authenticated,
    but does not raise an error if not. Returns None for anonymous users.
    """
    if not access_token:
        return None
    return auth_service.decode_access_token(access_token)