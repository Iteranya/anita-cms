# file: services/users.py

from typing import List, Dict
import bcrypt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from data import crud, schemas, models

# --- Password Hashing Setup (Replaces Passlib) ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed one using strict bcrypt.
    """
    # bcrypt.checkpw requires bytes, not strings.
    # We must encode the input strings to utf-8 bytes.
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hash_bytes)

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    Returns the hash as a string for database storage.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Decode back to utf-8 string so it can be saved in the SQL Text/String column
    return hashed_bytes.decode('utf-8')

# --- Service Class ---

class UserService:
    def __init__(self, db: Session):
        self.db = db

    # --- User Methods ---

    def get_user_by_username(self, username: str) -> models.User:
        """
        Gets a user by username, raising a standard 404 exception if not found.
        """
        user = crud.get_user_by_username(self.db, username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found."
            )
        return user

    def get_all_users(self) -> List[models.User]:
        """Gets a list of all users."""
        return crud.list_users(self.db)

    def create_user(self, user_in: schemas.UserCreateWithPassword) -> models.User:
        """
        Creates a new user.
        Handles password hashing and role validation.
        """
        # Business Logic 1: Check if username already exists.
        if crud.get_user_by_username(self.db, username=user_in.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{user_in.username}' is already registered."
            )

        # Business Logic 2: Check if the assigned role exists.
        if not crud.get_role(self.db, role_name=user_in.role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{user_in.role}' does not exist."
            )

        # Hash the password before storage.
        hashed_pw = hash_password(user_in.password)

        # Create the user data object for the CRUD layer.
        # Pydantic v2: Use model_dump instead of dict
        user_data_dict = user_in.model_dump(exclude={"password"})
        
        user_create_data = schemas.UserCreate(
            **user_data_dict,
            hashed_password=hashed_pw
        )
        
        return crud.save_user(self.db, user=user_create_data)

    def update_user(self, username: str, user_update: schemas.UserUpdate) -> models.User:
        """
        Updates a user's details.
        """
        # Ensure the user exists.
        db_user = self.get_user_by_username(username)
        
        # Business Logic: If a new role is being assigned, verify it exists.
        if user_update.role and not crud.get_role(self.db, role_name=user_update.role):
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{user_update.role}' does not exist."
            )

        # Get the update data from the Pydantic model.
        # Pydantic v2: Use model_dump instead of dict
        update_data = user_update.model_dump(exclude_unset=True)

        # Update the user model's attributes.
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
        
    def delete_user(self, username: str):
        """
        Deletes a user.
        """
        # Business Logic: Prevent deletion of the primary admin user.
        if username.lower() == 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete the primary admin user."
            )
            
        # Ensure user exists before trying to delete.
        self.get_user_by_username(username)
        crud.delete_user(self.db, username=username)

    # --- Role Methods ---

    def get_role_by_name(self, role_name: str) -> models.Role:
        """Gets a role by name, raising 404 if not found."""
        role = crud.get_role(self.db, role_name=role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found."
            )
        return role

    def get_all_roles(self) -> Dict[str, List[str]]:
        """Gets all roles and their permissions."""
        return crud.get_all_roles(self.db)

    def save_role(self, role_data: schemas.RoleCreate) -> models.Role:
        """
        Creates or updates a role.
        """
        # Business Logic: Prevent modification of the 'admin' role's core permission.
        if role_data.role_name == "admin" and role_data.permissions != ["*"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The 'admin' role must have the wildcard '*' permission."
            )
        return crud.save_role(self.db, role_name=role_data.role_name, permissions=role_data.permissions)

    def delete_role(self, role_name: str):
        """
        Deletes a role.
        """
        # Business Logic 1: Protect default roles from being deleted.
        protected_roles = {"admin", "editor", "viewer"}
        if role_name in protected_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot delete protected role: '{role_name}'."
            )
            
        # Ensure role exists.
        self.get_role_by_name(role_name)
        
        crud.delete_role(self.db, role_name=role_name)

    def get_user_permissions(self, username: str) -> List[str]:
        """
        Gets a list of all permissions for a specific user.
        """
        user = crud.get_user_by_username(self.db, username=username)
        if not user:
            return []

        user_role_name = user.role
        if not user_role_name:
            return []

        all_roles_with_permissions = self.get_all_roles()
        permissions = all_roles_with_permissions.get(user_role_name, [])
        
        return permissions