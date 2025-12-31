from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from data import models, schemas
from .labels import get_or_create_labels, apply_label_filters


def get_submission(db: Session, submission_id: int) -> Optional[models.Submission]:
    return db.query(models.Submission).filter(models.Submission.id == submission_id).first()

def list_submissions(db: Session, collection_slug: str, skip: int = 0, limit: int = 100) -> List[models.Submission]:
    return db.query(models.Submission).filter(models.Submission.collection_slug == collection_slug).order_by(models.Submission.created.desc()).offset(skip).limit(limit).all()

def search_submissions(db: Session, query_str: str) -> List[models.Submission]:
    query = db.query(models.Submission)
    query = apply_label_filters(query, models.Submission, query_str)
    return query.order_by(models.Submission.created.desc()).all()

def create_submission(db: Session, submission: schemas.SubmissionCreate) -> models.Submission:
    now = datetime.now(timezone.utc).isoformat()
    sub_data = submission.model_dump(exclude={'labels'})
    label_objects = get_or_create_labels(db, submission.labels)

    db_submission = models.Submission(**sub_data, created=now, updated=now)
    db_submission.labels = label_objects

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def update_submission(db: Session, submission_id: int, submission_update: schemas.SubmissionUpdate) -> Optional[models.Submission]:
    db_submission = get_submission(db, submission_id=submission_id)
    if not db_submission:
        return None
    
    update_data = submission_update.model_dump(exclude_unset=True)
    update_data.pop('collection_slug', None)
    
    if 'labels' in update_data:
        new_labels = update_data.pop('labels')
        if new_labels is not None:
            db_submission.labels = get_or_create_labels(db, new_labels)

    for key, value in update_data.items():
        setattr(db_submission, key, value)
    
    db_submission.updated =  datetime.now(timezone.utc).isoformat()
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