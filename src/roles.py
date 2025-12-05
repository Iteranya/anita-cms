import json
from pathlib import Path
from typing import List, Dict, Set

ROLES_FILE = "roles.json"

def get_roles_path() -> Path:
    return Path(ROLES_FILE)

def ensure_roles_file():
    if not get_roles_path().exists():
        # Default configuration
        defaults = {
            "admin": ["*"], # * means everything
            "editor": ["page:create", "page:update", "media:upload"],
            "viewer": ["page:read"]
        }
        with open(ROLES_FILE, 'w') as f:
            json.dump(defaults, f, indent=2)

def load_all_roles() -> Dict[str, List[str]]:
    ensure_roles_file()
    try:
        with open(ROLES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {}

def save_role(role_name: str, permissions: List[str]):
    data = load_all_roles()
    data[role_name] = permissions
    with open(ROLES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def delete_role_from_db(role_name: str):
    data = load_all_roles()
    if role_name in data:
        del data[role_name]
        with open(ROLES_FILE, "w") as f:
            json.dump(data, f, indent=2)

# --- THE PERMISSION CHECKER ---
def check_permission(user_role: str, required_perm: str) -> bool:
    """
    Checks if a role has a specific permission tag.
    Supports wildcard '*' for super-admins.
    """
    roles = load_all_roles()
    perms = roles.get(user_role, [])
    
    if "*" in perms:
        return True
    
    return required_perm in perms