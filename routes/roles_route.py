from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

# Import your auth logic
from src.auth import (
    require_admin, 
    load_all_users, 
    create_or_update_user, 
    get_user_by_username,
    save_user_data,
    get_password_hash
)
# Import the new role logic
from src.roles import load_all_roles, save_role, delete_role_from_db

router = APIRouter(prefix="/users", tags=["User & Role Management"])

# --- MODELS ---

class RoleModel(BaseModel):
    name: str
    permissions: List[str] # e.g. ["blog:create", "system:view"]

class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None

class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    password: Optional[str] = None # Optional password reset
    disabled: Optional[bool] = None

# ==========================================
# ROLE MANAGEMENT
# ==========================================

@router.get("/roles/", response_model=dict)
def get_roles(user: dict = Depends(require_admin)):
    """List all available roles and their permission tags."""
    return load_all_roles()

@router.post("/roles/")
def create_or_update_role(role_data: RoleModel, user: dict = Depends(require_admin)):
    """
    Create a new role or update permissions for an existing one.
    Example: name="editor", permissions=["page:create", "page:edit"]
    """
    if role_data.name == "admin" and "*" not in role_data.permissions:
        # Safety net: Don't let someone accidentally strip admin of power via API
        role_data.permissions.append("*")
        
    save_role(role_data.name, role_data.permissions)
    return {"message": f"Role '{role_data.name}' updated successfully"}

@router.delete("/roles/{role_name}")
def delete_role(role_name: str, user: dict = Depends(require_admin)):
    if role_name == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete the 'admin' role.")
    
    delete_role_from_db(role_name)
    return {"message": f"Role '{role_name}' deleted."}


# ==========================================
# USER MANAGEMENT
# ==========================================

@router.get("/")
def list_users(user: dict = Depends(require_admin)):
    """Returns a list of all users (hiding hash)."""
    users = load_all_users()
    clean_users = []
    for uname, data in users.items():
        # Create a safe copy without the password hash
        safe_data = data.copy()
        safe_data.pop("hashed_password", None)
        clean_users.append(safe_data)
    return clean_users

@router.post("/")
def register_new_user(new_user: UserCreateRequest, user: dict = Depends(require_admin)):
    """
    Admin manually creates a user.
    """
    # 1. Check if user exists
    if get_user_by_username(new_user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    # 2. Check if role exists
    existing_roles = load_all_roles()
    if new_user.role not in existing_roles:
        raise HTTPException(status_code=400, detail=f"Role '{new_user.role}' does not exist. Create it first.")

    # 3. Create
    create_or_update_user(
        username=new_user.username,
        password=new_user.password,
        role=new_user.role,
        display_name=new_user.display_name or new_user.username,
        pfp_url=new_user.pfp_url
    )
    return {"message": f"User '{new_user.username}' created."}

@router.put("/{target_username}")
def update_user(
    target_username: str, 
    update_data: UserUpdateRequest, 
    user: dict = Depends(require_admin)
):
    """
    Update a user's role, display name, or reset their password.
    """
    target_user = get_user_by_username(target_username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate Role if changing
    if update_data.role:
        existing_roles = load_all_roles()
        if update_data.role not in existing_roles:
            raise HTTPException(status_code=400, detail="Role does not exist")
        target_user["role"] = update_data.role

    # Update simple fields
    if update_data.display_name:
        target_user["display_name"] = update_data.display_name
    
    if update_data.pfp_url:
        target_user["pfp_url"] = update_data.pfp_url

    if update_data.disabled is not None:
        target_user["disabled"] = update_data.disabled

    # Password Reset
    if update_data.password:
        target_user["hashed_password"] = get_password_hash(update_data.password)

    # Save
    save_user_data(target_username, target_user)
    return {"message": f"User '{target_username}' updated."}

@router.delete("/{target_username}")
def delete_user(target_username: str, user: dict = Depends(require_admin)):
    # Prevent suicide (deleting your own account while logged in)
    if target_username == user["sub"]:
        raise HTTPException(status_code=400, detail="You cannot delete your own account while logged in.")

    # Load all data
    # (Note: src.auth doesn't have a specific delete function yet, so we do it manually here)
    from src.auth import SECRETS_FILE, ensure_secrets_file
    import json
    
    ensure_secrets_file()
    with open(SECRETS_FILE, "r") as f:
        data = json.load(f)
    
    if target_username not in data.get("users", {}):
        raise HTTPException(status_code=404, detail="User not found")
    
    del data["users"][target_username]
    
    with open(SECRETS_FILE, "w") as f:
        json.dump(data, f, indent=2)
        
    return {"message": f"User '{target_username}' deleted."}