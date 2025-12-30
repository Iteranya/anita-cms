from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from data import models, schemas
from .tags import get_or_create_tags, apply_tag_filters

def get_page(db: Session, slug: str) -> Optional[models.Page]:
    return db.query(models.Page).filter(models.Page.slug == slug).first()

def list_pages(db: Session, skip: int = 0, limit: int = 100) -> List[models.Page]:
    return db.query(models.Page).order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def search_pages(db: Session, query_str: str, skip: int = 0, limit: int = 100) -> List[models.Page]:
    query = db.query(models.Page)
    query = apply_tag_filters(query, models.Page, query_str)
    return query.order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def get_pages_by_tag(db: Session, tag: str, limit: int = 100) -> List[models.Page]:
    return search_pages(db, query_str=tag, limit=limit)

def get_pages_by_tags(db: Session, tags: List[str], match_all: bool = True, limit: int = 100) -> List[models.Page]:
    if not tags:
        return []
    if match_all:
        query_str = " ".join(tags)
        return search_pages(db, query_str=query_str, limit=limit)
    else:
        # Optimized OR logic: group_by ID instead of distinct() on text columns
        query = (
            db.query(models.Page)
            .join(models.Page.tags.property.secondary)
            .join(models.Tag)
            .filter(models.Tag.name.in_(tags))
            .group_by(models.Page.id) # Changed from .distinct() for performance
            .order_by(models.Page.created.desc())
            .limit(limit)
        )
        return query.all()
        
def get_first_page_by_tag(db: Session, tag: str) -> Optional[models.Page]:
    pages = get_pages_by_tag(db, tag, limit=1)
    return pages[0] if pages else None

def get_first_page_by_tags(db: Session, tag: List[str]) -> Optional[models.Page]:
    pages = get_pages_by_tags(db, tag, limit=1)
    return pages[0] if pages else None

def get_pages_by_author(db: Session, author: str, skip: int = 0, limit: int = 100) -> List[models.Page]:
    return db.query(models.Page).filter(models.Page.author == author).order_by(models.Page.created.desc()).offset(skip).limit(limit).all()

def create_page(db: Session, page: schemas.PageCreate) -> models.Page:
    now = datetime.now(timezone.utc).isoformat()
    page_data = page.model_dump(exclude={'tags'})
    tag_objects = get_or_create_tags(db, page.tags)
    
    db_page = models.Page(**page_data, created=now, updated=now)
    db_page.tags = tag_objects 
    
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
    
    if 'tags' in update_data:
        new_tags_list = update_data.pop('tags')
        if new_tags_list is not None:
            db_page.tags = get_or_create_tags(db, new_tags_list)

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