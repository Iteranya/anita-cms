from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from data import models, schemas
from .labels import get_or_create_labels

def get_form(db: Session, slug: str) -> Optional[models.Form]:
    return db.query(models.Form).filter(models.Form.slug == slug).first()

def list_forms(db: Session, skip: int = 0, limit: int = 100) -> List[models.Form]:
    return db.query(models.Form).order_by(models.Form.created.desc()).offset(skip).limit(limit).all()

def create_form(db: Session, form: schemas.FormCreate) -> models.Form:
    now = datetime.now(timezone.utc).isoformat()
    form_data = form.model_dump(by_alias=True, exclude={'labels'})
    label_objects = get_or_create_labels(db, form.labels)

    db_form = models.Form(**form_data, created=now, updated=now)
    db_form.labels = label_objects

    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form

def update_form(db: Session, slug: str, form_update: schemas.FormUpdate) -> Optional[models.Form]:
    db_form = get_form(db, slug=slug)
    if not db_form:
        return None

    update_data = form_update.model_dump(by_alias=True, exclude_unset=True)

    # --- ENFORCE IMMUTABLE SLUG ---
    update_data.pop('slug', None)

    if 'labels' in update_data:
        new_labels = update_data.pop('labels')
        if new_labels is not None:
            db_form.labels = get_or_create_labels(db, new_labels)

    for key, value in update_data.items():
        setattr(db_form, key, value)

    db_form.updated = datetime.now(timezone.utc).isoformat()
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