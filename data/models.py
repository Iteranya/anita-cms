# file: data/models.py

from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from dataclasses import dataclass
from .database import Base

class Page(Base):
    __tablename__ = "pages"

    slug = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    markdown = Column(Text)
    html = Column(Text)
    tags = Column(JSON)  # SQLAlchemy handles json.dumps/loads automatically
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
    schema = Column("schema_json", JSON, nullable=False) # Maps to schema_json column
    description = Column(Text)
    created = Column(String)
    updated = Column(String)
    author = Column(String)
    tags = Column(JSON)
    custom = Column(JSON)

    # Relationship to Submissions
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
    tags = Column(JSON, default=list) # <--- NEW: JSON column for list of strings

    # Relationship to Form
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
    value = Column(JSON, nullable=False) # Use JSON type for automatic handling

class Role(Base):
    __tablename__ = "roles"
    
    role_name = Column(String, primary_key=True)
    permissions = Column("permissions_json", JSON, nullable=False)

