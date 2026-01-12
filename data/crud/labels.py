from typing import List, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from data import models

def format_label_for_db(label: str) -> str:
    """Standardizes label strings (Danbooru style)."""
    if not label:
        return ""
    clean = label.strip().lower()
    clean = "_".join(clean.split())
    clean = clean.replace("<", "").replace(">", "")
    return clean

def get_or_create_labels(db: Session, label_list: List[str]) -> List[models.Label]:
    """Concurrency-Safe 'Get or Create'."""
    if not label_list:
        return []

    clean_names = set(format_label_for_db(t) for t in label_list if format_label_for_db(t))
    if not clean_names:
        return []

    existing_labels = db.query(models.Label).filter(models.Label.name.in_(clean_names)).all()
    existing_label_map = {t.name: t for t in existing_labels}
    final_labels = list(existing_labels)
    missing_names = clean_names - set(existing_label_map.keys())
    
    for name in missing_names:
        try:
            with db.begin_nested():
                new_label = models.Label(name=name)
                db.add(new_label)
                db.flush()
                final_labels.append(new_label)
        except IntegrityError:
            existing = db.query(models.Label).filter(models.Label.name == name).first()
            if existing:
                final_labels.append(existing)

    return final_labels

def parse_search_query(query_str: str):
    if not query_str:
        return [], []
    terms = query_str.split()
    included = set()
    excluded = set()
    for term in terms:
        clean_term = term.strip()
        if not clean_term:
            continue
        if clean_term.startswith('-') and len(clean_term) > 1:
            formatted = format_label_for_db(clean_term[1:])
            if formatted:
                excluded.add(formatted)
        else:
            formatted = format_label_for_db(clean_term)
            if formatted:
                included.add(formatted)
    return list(included), list(excluded)

def apply_label_filters(query: Query, model_class: Any, query_str: str) -> Query:
    if not query_str:
        return query
    included_labels, excluded_labels = parse_search_query(query_str)
    for label_name in excluded_labels:
        query = query.filter(~model_class.labels.any(models.Label.name == label_name))
    if included_labels:
        association_table = model_class.labels.property.secondary
        query = (
            query
            .join(association_table)
            .join(models.Label)
            .filter(models.Label.name.in_(included_labels))
            .group_by(model_class.id)
            .having(func.count(models.Label.id) == len(included_labels))
        )
    return query

def get_main_labels(db: Session) -> List[str]:
    """
    Retrieves all existing labels from the database that start with 'main:'.
    Returns a list of strings, e.g., ['main:blog', 'main:project'].
    """
    results = (
        db.query(models.Label.name)
        .filter(models.Label.name.startswith("main:"))
        .order_by(models.Label.name)
        .all()
    )
    
    # SQLAlchemy queries for specific columns return a list of tuples: [('main:blog',), ('main:p',)]
    # We flatten this into a simple list of strings.
    return [name for (name,) in results]