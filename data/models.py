# file: data/models.py

from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from .database import Base

# --- ASSOCIATION TABLES (The Glue) ---
# These are invisible tables that link items to tags.

page_tags = Table(
    'page_tags', Base.metadata,
    Column('page_slug', String, ForeignKey('pages.slug'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

form_tags = Table(
    'form_tags', Base.metadata,
    Column('form_id', Integer, ForeignKey('forms.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

submission_tags = Table(
    'submission_tags', Base.metadata,
    Column('submission_id', Integer, ForeignKey('submissions.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# --- THE TAG DICTIONARY ---

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) 
# --- MAIN MODELS ---

class Page(Base):
    __tablename__ = "pages"

    slug = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    markdown = Column(Text)
    html = Column(Text)
    
    # OLD: tags = Column(JSON)
    # NEW: Relationship
    tags = relationship("Tag", secondary=page_tags, backref="pages")
    
    thumb = Column(String)
    type = Column(String)
    created = Column(String)
    updated = Column(String)
    author = Column(String)
    custom = Column(JSON)

class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    schema = Column("schema_json", JSON, nullable=False)
    description = Column(Text)
    created = Column(String)
    updated = Column(String)
    author = Column(String)
    
    # OLD: tags = Column(JSON)
    # NEW: Relationship
    tags = relationship("Tag", secondary=form_tags, backref="forms")
    
    custom = Column(JSON)
    submissions = relationship("Submission", back_populates="form", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    form_slug = Column(String, ForeignKey("forms.slug", ondelete="CASCADE"), nullable=False)
    data = Column("submission_json", JSON, nullable=False)
    created = Column(String)
    updated = Column(String)
    author = Column(String)
    custom = Column(JSON)
    
    # OLD: tags = Column(JSON)
    # NEW: Relationship
    tags = relationship("Tag", secondary=submission_tags, backref="submissions")

    form = relationship("Form", back_populates="submissions")

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    display_name = Column(String)
    pfp_url = Column(String)
    disabled = Column(Boolean, nullable=False, default=False)

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(JSON, nullable=False)

class Role(Base):
    __tablename__ = "roles"
    
    role_name = Column(String, primary_key=True)
    permissions = Column("permissions_json", JSON, nullable=False)