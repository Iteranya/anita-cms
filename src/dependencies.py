# file: auth/dependencies.py

from typing import Optional
from fastapi import Depends, HTTPException, Request, status, Cookie
from sqlalchemy.orm import Session
from pydantic import ValidationError
from services.auth import AuthService
from services.users import UserService
from data.database import get_db
from data import schemas
from fastapi_csrf_protect import CsrfProtect

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService with a DB session."""
    user_service = UserService(db)
    return AuthService(user_service)

def csrf_protect_dependency( # This should be called 'Support Older Browser' Feature Instead of CSRF Feature
    request: Request, 
    csrf_protect: CsrfProtect = Depends()
):
    """
    A dependency that enforces CSRF protection on state-changing methods.
    
    It checks the request method. If it's a "safe" method (GET, HEAD, OPTIONS),
    it does nothing. For all other methods (POST, PUT, DELETE, PATCH), it
    validates the CSRF token. This dependency should be applied at the router level
    for all protected API endpoints.
    """
    safe_methods = {"GET", "HEAD", "OPTIONS"}
    
    if request.method.upper() not in safe_methods:
        csrf_protect.validate_csrf_in_request()


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
        print("No Access Token")
        # Raise an exception instead of returning None to enforce authentication
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = auth_service.decode_access_token(access_token)
    if not payload:
        print("No Payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        return schemas.CurrentUser(**payload)
    except ValidationError:
        print("Validation Error")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    


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
) -> Optional[schemas.CurrentUser]: 
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

config_access = require_permission("config:read") # Does not show keys
config_edit = require_permission("config:update")

# Aina Access
html_create = require_permission("html:create") # The Ability To Mark Page Type As HTML
html_read = require_permission("html:read") # The Ability To Open Aina Editor
html_update = require_permission("html:update") # The Ability To Save Aina Editor
html_delete = require_permission("html:delete") # Physically Impossible But Nice To Have

# Asta Access
markdown_create = require_permission("markdown:create") # The Ability To Mark Page Type As Markdown
markdown_read = require_permission("markdown:read") # The Ability To Open Asta Editor
markdown_update = require_permission("markdown:update")# The Ability To Save Asta Editor
markdown_delete = require_permission("markdown:delete") # Physically Impossible But Nice To Have

# Managing Blog Does NOT Require These Permissions 
# These are system level access to all pages in the CMS
page_create = require_permission("page:create")
page_read = require_permission("page:read")
page_update = require_permission("page:update")
page_delete = require_permission("page:delete")

# THESE ARE OVERRIDES
# By default, per form submission CRUD is managed by the Form's own labels
# It uses per-role basis, these ones are system level access to form's own permission
submission_create = require_permission("submission:create")
submission_read = require_permission("submission:read")
submission_update = require_permission("submission:update")
submission_delete = require_permission("submission:delete")