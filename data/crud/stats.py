from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from data import models
from .labels import format_label_for_db

def get_total_pages_count(db: Session) -> int:
    return db.query(func.count(models.Page.id)).scalar()

def get_total_forms_count(db: Session) -> int:
    return db.query(func.count(models.Form.id)).scalar()

def get_total_submissions_count(db: Session) -> int:
    return db.query(func.count(models.Submission.id)).scalar()

def get_total_users_count(db: Session) -> int:
    return db.query(func.count(models.User.username)).scalar()

def get_total_labels_count(db: Session) -> int:
    return db.query(func.count(models.Label.id)).scalar()

def get_pages_count_by_label(db: Session, label_name: str) -> int:
    formatted_label = format_label_for_db(label_name)
    return (
        db.query(func.count(models.Page.id))
        .join(models.Page.labels)
        .filter(models.Label.name == formatted_label)
        .scalar()
    )

def get_top_forms_by_submission_count(db: Session, limit: int = 5) -> List[Tuple[str, str, int]]:
    return (
        db.query(
            models.Form.title,                                               
            models.Form.slug,                                              
            func.count(models.Submission.id).label("submission_count")
        )
        .join(models.Submission, models.Form.slug == models.Submission.form_slug) 
        .group_by(models.Form.title, models.Form.slug)                      
        .order_by(func.count(models.Submission.id).desc())
        .limit(limit)
        .all()
    )

def get_top_labels_by_page_usage(db: Session, limit: int = 10) -> List[Tuple[str, int]]:
    return (
        db.query(
            models.Label.name,
            func.count(models.Page.id).label("use_count")
        )
        .join(models.Page.labels)
        .group_by(models.Label.name)
        .order_by(func.count(models.Page.id).desc())
        .limit(limit)
        .all()
    )

def get_recent_pages(db: Session, limit: int = 5) -> List[models.Page]:
    return db.query(models.Page).order_by(models.Page.created.desc()).limit(limit).all()

def get_recently_updated_pages(db: Session, limit: int = 5) -> List[models.Page]:
    return db.query(models.Page).order_by(models.Page.updated.desc()).limit(limit).all()

def get_recent_submissions(db: Session, limit: int = 5) -> List[models.Submission]:
    return db.query(models.Submission).order_by(models.Submission.created.desc()).limit(limit).all()