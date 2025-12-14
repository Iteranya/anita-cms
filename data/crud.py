from datetime import datetime
import json
from typing import List, Optional, Dict, Any, Type

from sqlalchemy.orm import Session, Query
from sqlalchemy import func, or_

# Import the SQLAlchemy models and Pydantic schemas
from data import models, schemas

# ==========================================
# --- SHARED TAGGING LOGIC (THE ENGINE) ---
# ==========================================

def format_tag_for_db(tag: str) -> str:
    """Standardizes tag strings. ' Cat ' -> '<cat>'"""
    clean = tag.strip().lower()
    clean = clean.replace("<", "").replace(">", "")
    return f"{clean}"

def get_or_create_tags(db: Session, tag_list: List[str]) -> List[models.Tag]:
    """
    Takes a list of strings ["news", "update"], finds them in the DB,
    creates them if missing, and returns the List of Tag Objects.
    """
    if not tag_list:
        return []

    tag_objects = []
    for tag_str in tag_list:
        clean_name = format_tag_for_db(tag_str)
        
        # Check if exists
        tag = db.query(models.Tag).filter(models.Tag.name == clean_name).first()
        
        # If not, create
        if not tag:
            tag = models.Tag(name=clean_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        
        tag_objects.append(tag)
        
    return tag_objects

def parse_search_query(query_str: str):
    """Parses 'cat -dog' into included and excluded lists."""
    if not query_str:
        return [], []
        
    terms = query_str.split()
    included = []
    excluded = []
    
    for term in terms:
        clean_term = term.strip()
        if clean_term.startswith('-') and len(clean_term) > 1:
            excluded.append(format_tag_for_db(clean_term[1:]))
        else:
            included.append(format_tag_for_db(clean_term))
            
    return included, excluded


def apply_tag_filters(query: Query, model_class: Any, query_str: str) -> Query:
    """
    Optimized tag filtering using JOIN + GROUP BY + HAVING.
    Dramatically faster for multiple inclusion tags.
    """
    if not query_str:
        return query

    included_tags, excluded_tags = parse_search_query(query_str)

    for tag_name in excluded_tags:
        query = query.filter(~model_class.tags.any(models.Tag.name == tag_name))

    if included_tags:
        # Get the association table (e.g., page_tags)
        association_table = model_class.tags.property.secondary
        
        query = (
            query
            .join(association_table)
            .join(models.Tag)
            .filter(models.Tag.name.in_(included_tags))
            .group_by(model_class.id)
            .having(func.count(models.Tag.id) == len(included_tags))
        )

    return query

# ==========================================
# --- PAGES FUNCTIONS ---
# ==========================================

def get_page(db: Session, slug: str) -> Optional[models.Page]:
    return db.query(models.Page).filter(models.Page.slug == slug).first()

def list_pages(db: Session, skip: int = 0, limit: int = 100) -> List[models.Page]:
    return db.query(models.Page).order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def search_pages(db: Session, query_str: str, skip: int = 0, limit: int = 100) -> List[models.Page]:
    """Optimized relational search."""
    query = db.query(models.Page)
    query = apply_tag_filters(query, models.Page, query_str)
    return query.order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def get_pages_by_tag(db: Session, tag: str, limit: int = 100) -> List[models.Page]:
    """Wrapper for search logic."""
    return search_pages(db, query_str=tag, limit=limit)

def get_pages_by_tags(
    db: Session, 
    tags: List[str], 
    match_all: bool = True,
    limit: int = 100
) -> List[models.Page]:
    """
    Fetch pages matching multiple tags.
    
    Args:
        db: Database session
        tags: List of tag names to filter by
        match_all: If True, pages must have ALL tags (AND logic).
                   If False, pages need ANY tag (OR logic).
        limit: Maximum number of results
    
    Returns:
        List of matching pages, newest first
    """
    if not tags:
        return []
    
    # Build query string for parse_search_query
    if match_all:
        # Space-separated = AND logic (all tags required)
        query_str = " ".join(tags)
    else:
        # OR logic: just grab pages with any of these tags
        query = (
            db.query(models.Page)
            .join(models.Page.tags.property.secondary)
            .join(models.Tag)
            .filter(models.Tag.name.in_(tags))
            .distinct()
            .order_by(models.Page.created.desc())
            .limit(limit)
        )
        return query.all()
    
    # Reuse your optimized search for AND logic
    return search_pages(db, query_str=query_str, limit=limit)


def get_first_page_by_tag(db: Session, tag: str) -> Optional[models.Page]:
    pages = get_pages_by_tag(db, tag, limit=1)
    return pages[0] if pages else None

def get_first_page_by_tags(db: Session, tag: List[str]) -> Optional[models.Page]:
    pages = get_pages_by_tags(db, tag, limit=1)
    return pages[0] if pages else None


def get_pages_by_author(
    db: Session,
    author: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.Page]:
    """Fetch pages by author, newest first."""
    return (
        db.query(models.Page)
        .filter(models.Page.author == author)
        .order_by(models.Page.created.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_page(db: Session, page: schemas.PageCreate) -> models.Page:
    now = datetime.now().isoformat()
    
    # 1. Prepare raw data (excluding tags)
    page_data = page.model_dump(exclude={'tags'})
    
    # 2. Convert string tags to Database Objects
    tag_objects = get_or_create_tags(db, page.tags)
    
    # 3. Create Page with Relationship
    db_page = models.Page(**page_data, created=now, updated=now)
    db_page.tags = tag_objects # SQLAlchemy handles the association table magic
    
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_page(db: Session, slug: str, page_update: schemas.PageUpdate) -> Optional[models.Page]:
    db_page = get_page(db, slug=slug)
    if not db_page:
        return None
    
    # Get dict of set values
    update_data = page_update.model_dump(exclude_unset=True)
    
    # Handle Tags specially if they exist in update data
    if 'tags' in update_data:
        new_tags_list = update_data.pop('tags')
        if new_tags_list is not None:
            # Replaces all existing tags with the new set
            db_page.tags = get_or_create_tags(db, new_tags_list)

    # Update other fields
    for key, value in update_data.items():
        setattr(db_page, key, value)
    
    db_page.updated = datetime.now().isoformat()
    db.commit()
    db.refresh(db_page)
    return db_page

def delete_page(db: Session, slug: str) -> bool:
    db_page = get_page(db, slug=slug)
    if db_page:
        db.delete(db_page)
        db.commit()
        return True
    return False

# ==========================================
# --- FORMS FUNCTIONS ---
# ==========================================

def get_form(db: Session, slug: str) -> Optional[models.Form]:
    return db.query(models.Form).filter(models.Form.slug == slug).first()

def list_forms(db: Session, skip: int = 0, limit: int = 100) -> List[models.Form]:
    return db.query(models.Form).order_by(models.Form.created.desc()).offset(skip).limit(limit).all()

def create_form(db: Session, form: schemas.FormCreate) -> models.Form:
    now = datetime.now().isoformat()
    
    form_data = form.model_dump(by_alias=True, exclude={'tags'})
    tag_objects = get_or_create_tags(db, form.tags)

    db_form = models.Form(**form_data, created=now, updated=now)
    db_form.tags = tag_objects

    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form

def update_form(db: Session, slug: str, form_update: schemas.FormUpdate) -> Optional[models.Form]:
    db_form = get_form(db, slug=slug)
    if not db_form:
        return None

    update_data = form_update.model_dump(by_alias=True, exclude_unset=True)

    if 'tags' in update_data:
        new_tags = update_data.pop('tags')
        if new_tags is not None:
            db_form.tags = get_or_create_tags(db, new_tags)

    for key, value in update_data.items():
        setattr(db_form, key, value)

    db_form.updated = datetime.now().isoformat()
    db.commit()
    db.refresh(db_form)
    return db_form

def delete_form(db: Session, slug: str) -> bool:
    db_form = get_form(db, slug=slug)
    if db_form:
        db.delete(db_form)
        db.commit()
        return True
    return False

# ==========================================
# --- SUBMISSIONS FUNCTIONS ---
# ==========================================

def get_submission(db: Session, submission_id: int) -> Optional[models.Submission]:
    return db.query(models.Submission).filter(models.Submission.id == submission_id).first()

def list_submissions(db: Session, form_slug: str, skip: int = 0, limit: int = 100) -> List[models.Submission]:
    return db.query(models.Submission).filter(models.Submission.form_slug == form_slug).order_by(models.Submission.created.desc()).offset(skip).limit(limit).all()

def search_submissions(db: Session, query_str: str) -> List[models.Submission]:
    """Search submissions by tag."""
    query = db.query(models.Submission)
    query = apply_tag_filters(query, models.Submission, query_str)
    return query.order_by(models.Submission.created.desc()).all()

def create_submission(db: Session, submission: schemas.SubmissionCreate) -> models.Submission:
    now = datetime.now().isoformat()
    
    sub_data = submission.model_dump(exclude={'tags'})
    tag_objects = get_or_create_tags(db, submission.tags)

    db_submission = models.Submission(**sub_data, created=now, updated=now)
    db_submission.tags = tag_objects

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def update_submission(db: Session, submission_id: int, submission_update: schemas.SubmissionUpdate) -> Optional[models.Submission]:
    db_submission = get_submission(db, submission_id=submission_id)
    if not db_submission:
        return None
    
    update_data = submission_update.model_dump(exclude_unset=True)
    
    if 'tags' in update_data:
        new_tags = update_data.pop('tags')
        if new_tags is not None:
            db_submission.tags = get_or_create_tags(db, new_tags)

    for key, value in update_data.items():
        setattr(db_submission, key, value)
    
    db_submission.updated = datetime.now().isoformat()
    db.commit()
    db.refresh(db_submission)
    return db_submission

def delete_submission(db: Session, submission_id: int) -> bool:
    db_submission = get_submission(db, submission_id=submission_id)
    if db_submission:
        db.delete(db_submission)
        db.commit()
        return True
    return False

# ==========================================
# --- USER / SETTINGS / ROLES (UNCHANGED) ---
# ==========================================

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

def get_setting(db: Session, key: str) -> Optional[Dict[str, Any]]:
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    return setting.value if setting else None

def get_all_settings(db: Session) -> Dict[str, Any]:
    settings = db.query(models.Setting).all()
    return {s.key: s.value for s in settings}

def save_setting(db: Session, key: str, value: Dict[str, Any]) -> models.Setting:
    db_setting = models.Setting(key=key, value=value)
    merged_setting = db.merge(db_setting)
    db.commit()
    return merged_setting

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

# ==========================================
# --- SEEDING (UPDATED FOR NEW TAGS) ---
# ==========================================

def seed_default_roles(db: Session, json_path: str = "default_roles.json"):
    if db.query(models.Role).count() == 0:
        print("No roles found. Seeding default roles.")
        try:
            with open(json_path, "r") as f:
                defaults = json.load(f)
            for role_name, permissions in defaults.items():
                save_role(db, role_name=role_name, permissions=permissions)
            print("✓ Default roles seeded.")
        except Exception as e:
            print(f"❌ Role seeding error: {e}")

def seed_default_pages(db: Session):
    if db.query(models.Page).count() > 0:
        return

    print("No pages found. Seeding default pages...")
    try:
        with open("default_pages.json", "r") as f:
            default_pages_data = json.load(f)
            
        for page_dict in default_pages_data:
            if not get_page(db, slug=page_dict['slug']):
                # IMPORTANT: We use schemas.PageCreate to validate
                # AND we use our create_page function to handle tag relation
                page_schema = schemas.PageCreate(**page_dict)
                create_page(db, page=page_schema)
                print(f"  - Created page: '{page_dict['title']}'")
        print("✓ Default pages seeded.")
    except Exception as e:
        print(f"Error seeding pages: {e}")

def seed_initial_settings(db: Session, json_path: str = "default_config.json"):
    if db.query(models.Setting).filter_by(key="system_note").first():
        return
    print("No settings found. Seeding defaults.")
    try:
        with open(json_path, "r") as f:
            default_settings = json.load(f)
        for key, value in default_settings.items():
            save_setting(db, key=key, value=value)
        print("✓ Default settings seeded.")
    except Exception as e:
        print(f"❌ Settings seeding error: {e}")