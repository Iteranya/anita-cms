# file: roles.py

from typing import List, Dict

# Import the central database module
from data import database

# --- REMOVED ---
# All file path logic (ROLES_FILE, get_roles_path, ensure_roles_file)
# and direct JSON handling (json.load, json.dump) have been removed.
# The database's get_connection() and seed_default_roles_db() handle this now.

def load_all_roles() -> Dict[str, List[str]]:
    """Loads all roles from the central database."""
    return database.get_all_roles_db()

def save_role(role_name: str, permissions: List[str]):
    """Saves a single role and its permissions to the database."""
    database.save_role_db(role_name, permissions)

def delete_role(role_name: str):
    """Deletes a role from the database."""
    database.delete_role_db(role_name)

# --- THE PERMISSION CHECKER ---
# This function's logic is unchanged, but its data source is now the database
# via the refactored load_all_roles() function.
def check_permission(user_role: str, required_perm: str) -> bool:
    """
    Checks if a user's role has a specific permission.
    Supports wildcard '*' for super-admins.
    """
    all_roles = load_all_roles()
    
    # Get the permissions for the user's specific role, default to an empty list
    user_permissions = all_roles.get(user_role, [])
    
    # The admin wildcard grants all permissions
    if "*" in user_permissions:
        return True
    
    # Otherwise, check if the specific permission exists in their list
    return required_perm in user_permissions