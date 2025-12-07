from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

# Import the SQLAlchemy models and Pydantic schemas
from data import models, schemas

# --- Pages Functions ---

def get_page(db: Session, slug: str) -> Optional[models.Page]:
    """Retrieve a single page by its slug."""
    return db.query(models.Page).filter(models.Page.slug == slug).first()

def list_pages(db: Session, skip: int = 0, limit: int = 100) -> List[models.Page]:
    """Retrieve all pages with pagination."""
    return db.query(models.Page).order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def get_pages_by_tag(db: Session, tag: str) -> List[models.Page]:
    """Retrieve all pages containing a specific tag in their JSON tags list."""
    # The .contains() operator is a powerful feature for JSON columns in SQLAlchemy
    return db.query(models.Page).filter(models.Page.tags.contains(tag)).order_by(models.Page.created.desc()).all()

def get_first_page_by_tag(db: Session, tag: str) -> Optional[models.Page]:
    """Retrieve the most recent page with a specific tag."""
    return db.query(models.Page).filter(models.Page.tags.contains(tag)).order_by(models.Page.created.desc()).first()

def create_page(db: Session, page: schemas.PageCreate) -> models.Page:
    """Create a new page."""
    now = datetime.now().isoformat()
    db_page = models.Page(**page.dict(), created=now, updated=now)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_page(db: Session, slug: str, page_update: schemas.PageUpdate) -> Optional[models.Page]:
    """Update an existing page."""
    db_page = get_page(db, slug=slug)
    if not db_page:
        return None
    
    update_data = page_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_page, key, value)
    
    db_page.updated = datetime.now().isoformat()
    db.commit()
    db.refresh(db_page)
    return db_page

def delete_page(db: Session, slug: str) -> bool:
    """Delete a page by its slug. Returns True if deleted, False otherwise."""
    db_page = get_page(db, slug=slug)
    if db_page:
        db.delete(db_page)
        db.commit()
        return True
    return False

# --- Forms Functions ---

def get_form(db: Session, slug: str) -> Optional[models.Form]:
    """Retrieve a single form by its slug."""
    return db.query(models.Form).filter(models.Form.slug == slug).first()

def list_forms(db: Session, skip: int = 0, limit: int = 100) -> List[models.Form]:
    """Retrieve all forms with pagination."""
    return db.query(models.Form).order_by(models.Form.created.desc()).offset(skip).limit(limit).all()

def create_form(db: Session, form: schemas.FormCreate) -> models.Form:
    """Create a new form."""
    now = datetime.now().isoformat()
    # The Pydantic schema uses 'schema', the model uses 'schema_'. We handle it here.
    form_data = form.dict()
    db_form = models.Form(
        **form_data,
        schema_=form_data.pop('schema'),
        created=now,
        updated=now
    )
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form

def update_form(db: Session, slug: str, form_update: schemas.FormUpdate) -> Optional[models.Form]:
    """Update an existing form."""
    db_form = get_form(db, slug=slug)
    if not db_form:
        return None
    
    update_data = form_update.dict(exclude_unset=True)
    # Handle the 'schema' to 'schema_' mapping
    if 'schema' in update_data:
        setattr(db_form, 'schema_', update_data.pop('schema'))
        
    for key, value in update_data.items():
        setattr(db_form, key, value)
    
    db_form.updated = datetime.now().isoformat()
    db.commit()
    db.refresh(db_form)
    return db_form

def delete_form(db: Session, slug: str) -> bool:
    """Delete a form. Associated submissions are deleted automatically by the database cascade."""
    db_form = get_form(db, slug=slug)
    if db_form:
        db.delete(db_form)
        db.commit()
        return True
    return False

# --- Submissions Functions ---

def get_submission(db: Session, submission_id: int) -> Optional[models.Submission]:
    """Retrieve a single submission by its ID."""
    return db.query(models.Submission).filter(models.Submission.id == submission_id).first()

def list_submissions(db: Session, form_slug: str, skip: int = 0, limit: int = 100) -> List[models.Submission]:
    """List all submissions for a given form slug, with pagination."""
    return db.query(models.Submission).filter(models.Submission.form_slug == form_slug).order_by(models.Submission.created.desc()).offset(skip).limit(limit).all()

def create_submission(db: Session, submission: schemas.SubmissionCreate) -> models.Submission:
    """Create a new form submission."""
    now = datetime.now().isoformat()
    db_submission = models.Submission(
        **submission.dict(),
        created=now,
        updated=now
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def update_submission(db: Session, submission_id: int, submission_update: schemas.SubmissionUpdate) -> Optional[models.Submission]:
    """Update an existing submission's data or custom fields."""
    db_submission = get_submission(db, submission_id=submission_id)
    if not db_submission:
        return None
    
    update_data = submission_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_submission, key, value)
    
    db_submission.updated = datetime.now().isoformat()
    db.commit()
    db.refresh(db_submission)
    return db_submission

def delete_submission(db: Session, submission_id: int) -> bool:
    """Delete a submission by its ID."""
    db_submission = get_submission(db, submission_id=submission_id)
    if db_submission:
        db.delete(db_submission)
        db.commit()
        return True
    return False

# --- User Functions ---

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Retrieve a single user by their username."""
    return db.query(models.User).filter(models.User.username == username).first()

def list_users(db: Session) -> List[models.User]:
    """Retrieve all users."""
    return db.query(models.User).order_by(models.User.username).all()

def count_users(db: Session) -> int:
    """Count the total number of users."""
    return db.query(models.User).count()

def save_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create or update a user (upsert)."""
    db_user = models.User(**user.dict())
    # merge() handles both INSERT and UPDATE. It checks the primary key.
    merged_user = db.merge(db_user)
    db.commit()
    return merged_user

def delete_user(db: Session, username: str) -> bool:
    """Delete a user by username."""
    db_user = get_user_by_username(db, username=username)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# --- Settings Functions ---

def get_setting(db: Session, key: str) -> Optional[Dict[str, Any]]:
    """Retrieve a setting's value by its key."""
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    return setting.value if setting else None

def get_all_settings(db: Session) -> Dict[str, Any]:
    """Retrieve all settings as a key-value dictionary."""
    settings = db.query(models.Setting).all()
    return {s.key: s.value for s in settings}

def save_setting(db: Session, key: str, value: Dict[str, Any]) -> models.Setting:
    """Create or update a setting (upsert)."""
    db_setting = models.Setting(key=key, value=value)
    merged_setting = db.merge(db_setting)
    db.commit()
    return merged_setting

# --- Roles Functions ---

def get_role(db: Session, role_name: str) -> Optional[models.Role]:
    """Retrieve a single role by name."""
    return db.query(models.Role).filter(models.Role.role_name == role_name).first()

def get_all_roles(db: Session) -> Dict[str, List[str]]:
    """Retrieve all roles and their permissions as a dictionary."""
    roles = db.query(models.Role).all()
    return {role.role_name: role.permissions for role in roles}

def save_role(db: Session, role_name: str, permissions: List[str]) -> models.Role:
    """Create or update a role and its permissions (upsert)."""
    db_role = models.Role(role_name=role_name, permissions=permissions)
    merged_role = db.merge(db_role)
    db.commit()
    return merged_role

def delete_role(db: Session, role_name: str) -> bool:
    """Delete a role by name."""
    db_role = get_role(db, role_name)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False

def seed_default_roles(db: Session):
    """Adds default roles and permissions if no roles exist in the database."""
    if db.query(models.Role).count() == 0:
        print("No roles found in database. Seeding default roles.")
        defaults = {
            "admin": ["*"],
            "editor": ["page:create", "page:update", "media:upload"],
            "viewer": ["page:read"]
        }
        for role_name, permissions in defaults.items():
            save_role(db, role_name=role_name, permissions=permissions)
        print("✓ Default roles seeded.")