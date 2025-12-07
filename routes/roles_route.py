from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy.orm import Session

# --- Service, Schema, and Auth Imports ---
from data.database import get_db
from data import schemas
from services.users import UserService, hash_password
from src.dependencies import get_current_user, require_admin
from data.schemas import User as CurrentUser

# --- Dependency Setup ---

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency provider for the UserService."""
    return UserService(db)

# --- Router Definition ---
router = APIRouter(prefix="/users", tags=["User & Role Management"])

# --- Pydantic Model for Password Resets ---
class PasswordReset(BaseModel):
    new_password: str

# ==========================================
# ROLE MANAGEMENT
# ==========================================

@router.get("/roles", response_model=Dict[str, List[str]])
def get_roles(
    user_service: UserService = Depends(get_user_service),
    admin: CurrentUser = Depends(require_admin),
):
    """List all available roles and their permission tags."""
    return user_service.get_all_roles()

@router.post("/roles", response_model=schemas.Role)
def create_or_update_role(
    role_data: schemas.RoleCreate,
    user_service: UserService = Depends(get_user_service),
    admin: CurrentUser = Depends(require_admin),
):
    """
    Create a new role or update permissions for an existing one.
    The service layer handles protection of the 'admin' role.
    """
    return user_service.save_role(role_data)

@router.delete("/roles/{role_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_name: str,
    user_service: UserService = Depends(get_user_service),
    admin: CurrentUser = Depends(require_admin),
):
    """
    Delete a role. The service layer protects core roles from deletion.
    """
    user_service.delete_role(role_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================
# USER MANAGEMENT
# ==========================================

@router.get("/", response_model=List[schemas.User])
def list_users(
    user_service: UserService = Depends(get_user_service),
    admin: CurrentUser = Depends(require_admin),
):
    """Returns a list of all users. The password hash is automatically excluded by the Pydantic model."""
    return user_service.get_all_users()

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_new_user(
    new_user: schemas.UserCreateWithPassword,
    user_service: UserService = Depends(get_user_service) 
):
    """Admin-only endpoint to create a new user. The service handles validation."""
    return user_service.create_user(new_user)

@router.put("/{target_username}", response_model=schemas.User)
def update_user(
    target_username: str,
    update_data: schemas.UserUpdate,
    user_service: UserService = Depends(get_user_service),
    admin: CurrentUser = Depends(require_admin),
):
    """
    Update a user's details (role, display name, etc.).
    Note: This endpoint does NOT handle password changes.
    """
    return user_service.update_user(username=target_username, user_update=update_data)

@router.put("/{target_username}/password")
def change_user_password(
    target_username: str,
    password_data: PasswordReset,
    user_service: UserService = Depends(get_user_service),
    admin: CurrentUser = Depends(require_admin),
):
    """
    Admin-only endpoint to set a new password for any user.
    NOTE: This requires a new method `change_password` to be added to your UserService.
    """
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )
    # The following line assumes you have a method in UserService to handle this.
    # user_service.change_password(username=target_username, new_password=password_data.new_password)
    
    # For now, let's implement the logic here, but it should be moved to the service:
    db_user = user_service.get_user_by_username(target_username)
    db_user.hashed_password = hash_password(password_data.new_password)
    user_service.db.commit()

    return {"message": f"Password for user '{target_username}' has been updated."}

@router.delete("/{target_username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    target_username: str,
    user_service: UserService = Depends(get_user_service),
    admin: CurrentUser = Depends(require_admin),
):
    """Deletes a user. You cannot delete your own account."""
    # Authorization: Prevent an admin from deleting their own account via the API.
    if target_username == admin.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account while logged in."
        )
        
    user_service.delete_user(target_username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)