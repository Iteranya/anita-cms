from datetime import datetime
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy import String, cast
from sqlalchemy.orm import Session

# Import the SQLAlchemy models and Pydantic schemas
from data import models, schemas

# --- Utility Functions (Because SQLite Is Stupid) ---
def format_tag_for_db(tag: str) -> str:
    """Formats 'Cat' into '<cat>'."""
    clean = tag.strip().lower()
    # Prevent double brackets if data is dirty
    clean = clean.replace("<", "").replace(">", "")
    return f"<{clean}>"

def parse_search_query(query_str: str):
    """
    Parses 'cat -dog' into:
    included: ['<cat>']
    excluded: ['<dog>']
    """
    if not query_str:
        return [], []
        
    terms = query_str.split()
    included = []
    excluded = []
    
    for term in terms:
        clean_term = term.strip()
        if clean_term.startswith('-') and len(clean_term) > 1:
            # Exclude
            excluded.append(format_tag_for_db(clean_term[1:]))
        else:
            # Include
            included.append(format_tag_for_db(clean_term))
            
    return included, excluded

# --- Pages Functions ---

def get_page(db: Session, slug: str) -> Optional[models.Page]:
    """Retrieve a single page by its slug."""
    return db.query(models.Page).filter(models.Page.slug == slug).first()

def list_pages(db: Session, skip: int = 0, limit: int = 100) -> List[models.Page]:
    """Retrieve all pages with pagination."""
    return db.query(models.Page).order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def search_pages(
    db: Session, 
    query_str: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.Page]:
    """
    Search pages with inclusion and exclusion.
    Works on SQLite and Postgres.
    Input: "cat -dog"
    """
    query = db.query(models.Page)
    
    if query_str:
        included_tags, excluded_tags = parse_search_query(query_str)
        
        # Cast JSON column to String for universal text searching
        # Postgres: JSONB -> Text
        # SQLite: JSON -> String
        tags_as_string = cast(models.Page.tags, String)

        # 1. Handle Inclusion (AND)
        for tag in included_tags:
            # JSON arrays store strings in double quotes: ["<tag>"]
            # We search for the pattern including quotes for safety
            search_pat = f'%"{tag}"%' 
            query = query.filter(tags_as_string.ilike(search_pat))

        # 2. Handle Exclusion (NOT)
        for tag in excluded_tags:
            search_pat = f'%"{tag}"%'
            query = query.filter(~tags_as_string.ilike(search_pat))

    # Standard Sort
    query = query.order_by(models.Page.created.desc())
    
    return query.offset(skip).limit(limit).all()

def get_pages_by_tag(db: Session, tag: str) -> List[models.Page]:
    """Retrieve all pages containing a specific tag in their JSON tags list,
    with input validation and post-query verification."""
    
    if not isinstance(tag, str) or not tag.strip():
        raise ValueError("Tag must be a non-empty string.")

    # Initial DB-level filtering (efficient but may require verification)
    candidates = (
        db.query(models.Page)
        .filter(models.Page.tags.contains([tag]))   # safer than contains(tag) if tags is a list
        .all()
    )

    # Double-check tags actually contain the requested tag
    valid_pages = [p for p in candidates if isinstance(p.tags, list) and tag in p.tags]

    # Sort newest first
    valid_pages.sort(key=lambda x: x.created, reverse=True)

    return valid_pages
    
def get_first_page_by_tag(db: Session, tag: str) -> Optional[models.Page]:
    candidates = db.query(models.Page).filter(models.Page.tags.contains(tag)).all()
    valid_pages = [p for p in candidates if tag in p.tags]
    valid_pages.sort(key=lambda x: x.created, reverse=True)
    return valid_pages[0] if valid_pages else None

  

def create_page(db: Session, page: schemas.PageCreate) -> models.Page:
    """Create a new page."""
    formatted_tags = [format_tag_for_db(t) for t in page.tags]
    page_data = page.dict()
    page_data['tags'] = formatted_tags
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
    
    if 'tags' in update_data and update_data['tags'] is not None:
        update_data['tags'] = [format_tag_for_db(t) for t in update_data['tags']]
    
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
    form_data = form.model_dump(by_alias=True)

    db_form = models.Form(
        **form_data,
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

    # Use by_alias=True and exclude_unset=True to only get updated fields with correct names.
    update_data = form_update.model_dump(by_alias=True, exclude_unset=True)

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


def seed_default_roles(db: Session, json_path: str = "default_roles.json"):
    """Adds default roles and permissions if no roles exist in the database."""
    if db.query(models.Role).count() == 0:
        print("No roles found in database. Seeding default roles.")

        try:
            with open(json_path, "r") as f:
                defaults = json.load(f)

        except Exception as e:
            print(f"❌ Unexpected error loading role seeds: {e}")
            return

        # Insert roles into DB
        for role_name, permissions in defaults.items():
            try:
                save_role(db, role_name=role_name, permissions=permissions)
            except Exception as e:
                print(f"❌ Failed to save role '{role_name}': {e}")

        print("✓ Default roles seeded.")



def seed_default_pages(db: Session):
    """
    Adds default pages from a JSON file if no pages exist in the database.
    This function is idempotent and safe to run on every application startup.
    """
    # 1. Check if any pages already exist to prevent re-seeding.
    if db.query(models.Page).count() > 0:
        # Optional: You could add a log or print statement here for debugging.
        # print("Pages table is not empty. Skipping seeding.")
        return

    print("No pages found in database. Seeding default pages...")
    
    # 2. Locate and load the default pages data.
    try:
        pages_file = "default_pages.json"
        with open(pages_file, "r") as f:
            default_pages_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading default_pages.json: {e}. Skipping page seeding.")
        return

    # 3. Iterate, validate with Pydantic, and create each page.
    for page_dict in default_pages_data:
        # Check if a page with this slug already exists (extra safety).
        if not get_page(db, slug=page_dict['slug']):
            # Use the Pydantic schema to create a validated object
            page_schema = schemas.PageCreate(**page_dict)
            # Use your existing CRUD function to create the page
            create_page(db, page=page_schema)
            print(f"  - Created page: '{page_dict['title']}' ({page_dict['slug']})")

    print("✓ Default pages seeded.")

def seed_initial_settings(db: Session, json_path: str = "default_config.json"):
    """
    Adds default settings from a JSON file if no settings exist in the database.
    This function is idempotent and follows the same pattern as other seeders.
    """
    # 1. Check if a core setting already exists to prevent re-seeding.
    if db.query(models.Setting).filter_by(key="system_note").first():
        return

    print("No settings found in database. Seeding initial application configuration.")

    # 2. Locate and load the default settings data from the JSON file.
    try:
        with open(json_path, "r") as f:
            default_settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading {json_path}: {e}. Skipping settings seeding.")
        return

    # 3. Iterate and save each setting.
    for key, value in default_settings.items():
        try:
            save_setting(db, key=key, value=value)
        except Exception as e:
            print(f"❌ Failed to save setting '{key}': {e}")
            
    print("✓ Default settings seeded.")
