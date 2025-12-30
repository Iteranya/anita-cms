from typing import List, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from data import models

def format_tag_for_db(tag: str) -> str:
    """Standardizes tag strings (Danbooru style)."""
    if not tag:
        return ""
    clean = tag.strip().lower()
    clean = "_".join(clean.split())
    clean = clean.replace("<", "").replace(">", "")
    return clean

def get_or_create_tags(db: Session, tag_list: List[str]) -> List[models.Tag]:
    """Concurrency-Safe 'Get or Create'."""
    if not tag_list:
        return []

    clean_names = set(format_tag_for_db(t) for t in tag_list if format_tag_for_db(t))
    if not clean_names:
        return []

    existing_tags = db.query(models.Tag).filter(models.Tag.name.in_(clean_names)).all()
    existing_tag_map = {t.name: t for t in existing_tags}
    final_tags = list(existing_tags)
    missing_names = clean_names - set(existing_tag_map.keys())
    
    for name in missing_names:
        try:
            with db.begin_nested():
                new_tag = models.Tag(name=name)
                db.add(new_tag)
                db.flush()
                final_tags.append(new_tag)
        except IntegrityError:
            existing = db.query(models.Tag).filter(models.Tag.name == name).first()
            if existing:
                final_tags.append(existing)

    return final_tags

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
            formatted = format_tag_for_db(clean_term[1:])
            if formatted:
                excluded.add(formatted)
        else:
            formatted = format_tag_for_db(clean_term)
            if formatted:
                included.add(formatted)
    return list(included), list(excluded)

def apply_tag_filters(query: Query, model_class: Any, query_str: str) -> Query:
    if not query_str:
        return query
    included_tags, excluded_tags = parse_search_query(query_str)
    for tag_name in excluded_tags:
        query = query.filter(~model_class.tags.any(models.Tag.name == tag_name))
    if included_tags:
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

def get_main_tags(db: Session) -> List[str]:
    """
    Retrieves all existing tags from the database that start with 'main:'.
    Returns a list of strings, e.g., ['main:blog', 'main:project'].
    """
    results = (
        db.query(models.Tag.name)
        .filter(models.Tag.name.startswith("main:"))
        .order_by(models.Tag.name)
        .all()
    )
    
    # SQLAlchemy queries for specific columns return a list of tuples: [('main:blog',), ('main:p',)]
    # We flatten this into a simple list of strings.
    return [name for (name,) in results]