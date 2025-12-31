from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from data import models, schemas
from .labels import get_or_create_labels, apply_label_filters

def get_page(db: Session, slug: str) -> Optional[models.Page]:
    return db.query(models.Page).filter(models.Page.slug == slug).first()

def list_pages(db: Session, skip: int = 0, limit: int = 100) -> List[models.Page]:
    return db.query(models.Page).order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def search_pages(db: Session, query_str: str, skip: int = 0, limit: int = 100) -> List[models.Page]:
    query = db.query(models.Page)
    query = apply_label_filters(query, models.Page, query_str)
    return query.order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def get_pages_by_label(db: Session, label: str, limit: int = 100) -> List[models.Page]:
    return search_pages(db, query_str=label, limit=limit)

def get_pages_by_labels(db: Session, labels: List[str], match_all: bool = True, limit: int = 100) -> List[models.Page]:
    if not labels:
        return []
    if match_all:
        query_str = " ".join(labels)
        return search_pages(db, query_str=query_str, limit=limit)
    else:
        # Optimized OR logic: group_by ID instead of distinct() on text columns
        query = (
            db.query(models.Page)
            .join(models.Page.labels.property.secondary)
            .join(models.Label)
            .filter(models.Label.name.in_(labels))
            .group_by(models.Page.id) # Changed from .distinct() for performance
            .order_by(models.Page.created.desc())
            .limit(limit)
        )
        return query.all()
        
def get_first_page_by_label(db: Session, label: str) -> Optional[models.Page]:
    pages = get_pages_by_label(db, label, limit=1)
    return pages[0] if pages else None

def get_first_page_by_labels(db: Session, label: List[str]) -> Optional[models.Page]:
    pages = get_pages_by_labels(db, label, limit=1)
    return pages[0] if pages else None

def get_pages_by_author(db: Session, author: str, skip: int = 0, limit: int = 100) -> List[models.Page]:
    return db.query(models.Page).filter(models.Page.author == author).order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def create_page(db: Session, page: schemas.PageCreate) -> models.Page:
    now = datetime.now(timezone.utc).isoformat()
    page_data = page.model_dump(exclude={'labels'})
    label_objects = get_or_create_labels(db, page.labels)
    
    db_page = models.Page(**page_data, created=now, updated=now)
    db_page.labels = label_objects 
    
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_page(db: Session, slug: str, page_update: schemas.PageUpdate) -> Optional[models.Page]:
    db_page = get_page(db, slug=slug)
    if not db_page:
        return None
    
    update_data = page_update.model_dump(exclude_unset=True)
    
    # --- ENFORCE IMMUTABLE SLUG ---
    # Even if the API request sent a new slug, we silently remove it.
    update_data.pop('slug', None)
    
    if 'labels' in update_data:
        new_labels_list = update_data.pop('labels')
        if new_labels_list is not None:
            db_page.labels = get_or_create_labels(db, new_labels_list)

    for key, value in update_data.items():
        setattr(db_page, key, value)
    
    db_page.updated = datetime.now(timezone.utc).isoformat()
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