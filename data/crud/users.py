from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from data import models, schemas

# --- USERS ---

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def list_users(db: Session) -> List[models.User]:
    return db.query(models.User).order_by(models.User.username).all()

def count_users(db: Session) -> int:
    return db.query(models.User).count()

def save_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.dict())
    merged_user = db.merge(db_user)
    db.commit()
    return merged_user

def delete_user(db: Session, username: str) -> bool:
    db_user = get_user_by_username(db, username=username)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# --- ROLES ---

def get_role(db: Session, role_name: str) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.role_name == role_name).first()

def get_all_roles(db: Session) -> Dict[str, List[str]]:
    roles = db.query(models.Role).all()
    return {role.role_name: role.permissions for role in roles}

def save_role(db: Session, role_name: str, permissions: List[str]) -> models.Role:
    db_role = models.Role(role_name=role_name, permissions=permissions)
    merged_role = db.merge(db_role)
    db.commit()
    return merged_role

def delete_role(db: Session, role_name: str) -> bool:
    db_role = get_role(db, role_name)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False