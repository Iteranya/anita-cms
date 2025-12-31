from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from data import models, schemas
from .labels import get_or_create_labels

def get_collection(db: Session, slug: str) -> Optional[models.Collection]:
    return db.query(models.Collection).filter(models.Collection.slug == slug).first()

def list_collections(db: Session, skip: int = 0, limit: int = 100) -> List[models.Collection]:
    return db.query(models.Collection).order_by(models.Collection.created.desc()).offset(skip).limit(limit).all()

def create_collection(db: Session, collection: schemas.CollectionCreate) -> models.Collection:
    now = datetime.now(timezone.utc).isoformat()
    collection_data = collection.model_dump(by_alias=True, exclude={'labels'})
    label_objects = get_or_create_labels(db, collection.labels)

    db_collection = models.Collection(**collection_data, created=now, updated=now)
    db_collection.labels = label_objects

    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

def update_collection(db: Session, slug: str, collection_update: schemas.CollectionUpdate) -> Optional[models.Collection]:
    db_collection = get_collection(db, slug=slug)
    if not db_collection:
        return None

    update_data = collection_update.model_dump(by_alias=True, exclude_unset=True)

    # --- ENFORCE IMMUTABLE SLUG ---
    update_data.pop('slug', None)

    if 'labels' in update_data:
        new_labels = update_data.pop('labels')
        if new_labels is not None:
            db_collection.labels = get_or_create_labels(db, new_labels)

    for key, value in update_data.items():
        setattr(db_collection, key, value)

    db_collection.updated = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_collection)
    return db_collection

def delete_collection(db: Session, slug: str) -> bool:
    db_collection = get_collection(db, slug=slug)
    if db_collection:
        db.delete(db_collection)
        db.commit()
        return True
    return False