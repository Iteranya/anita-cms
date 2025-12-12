# file: auth/dependencies.py

from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from pydantic import ValidationError
from services.auth import AuthService
from services.users import UserService
from data.database import get_db
from data import schemas

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService with a DB session."""
    user_service = UserService(db)
    return AuthService(user_service)

def get_current_user(
    access_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> schemas.CurrentUser:
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
    

# List All Specific Permissions Here
# Well, most aren't use since it's granular, but...
# Eh, it's good to show what exists and what not
require_admin = require_permission("*") 

form_create = require_permission("form:create")
form_read = require_permission("form:read")
form_update = require_permission("form:update")
form_delete = require_permission("form:delete")

media_create = require_permission("media:create")
media_read = require_permission("media:read") # List all media perm, by default, all media can be accessed publicly
media_update = require_permission("media:update") # Media Meta Data Edit
media_delete = require_permission("media:delete")

blog_create = require_permission("blog:create")
blog_read = require_permission("blog:read")
blog_update = require_permission("blog:update")
blog_delete = require_permission("blog:delete")

config_access = require_permission("config:read") # Does not show keys
config_edit = require_permission("config:update")

aina_access = require_permission("aina") # Access Aina AI, manipulation follows page crud perms
asta_access = require_permission("asta") # Access Asta AI, manipulation follows blog crud perms

# Managing Blog Does NOT Require These Permissions 
# These are system level access to all pages in the CMS
page_create = require_permission("page:create")
page_read = require_permission("page:read")
page_update = require_permission("page:update")
page_delete = require_permission("page:delete")

# THESE ARE OVERRIDES
# By default, per form submission CRUD is managed by the Form's own tags
# It uses per-role basis, these ones are system level access to form's own permission
submission_create = require_permission("submission:create")
submission_read = require_permission("submission:read")
submission_update = require_permission("submission:update")
submission_delete = require_permission("submission:delete")