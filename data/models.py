# file: data/models.py

from sqlalchemy import Column, Index, Integer, String, Text, JSON, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from .database import Base

# --- ASSOCIATION TABLES ---

page_labels = Table(
    'page_labels', Base.metadata,
    Column('page_slug', String, ForeignKey('pages.slug'), primary_key=True),
    Column('label_id', Integer, ForeignKey('labels.id'), primary_key=True)
)

form_labels = Table(
    'form_labels', Base.metadata,
    Column('form_id', Integer, ForeignKey('forms.id'), primary_key=True),
    Column('label_id', Integer, ForeignKey('labels.id'), primary_key=True)
)

submission_labels = Table(
    'submission_labels', Base.metadata,
    Column('submission_id', Integer, ForeignKey('submissions.id'), primary_key=True),
    Column('label_id', Integer, ForeignKey('labels.id'), primary_key=True)
)

# --- THE TAG DICTIONARY ---

class Label(Base):
    __tablename__ = 'labels'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) 
# --- MAIN MODELS ---

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    markdown = Column(Text)
    html = Column(Text)
    labels = relationship("Label", secondary=page_labels, backref="pages")
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
    labels = relationship("Label", secondary=form_labels, backref="forms")
    
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
    labels = relationship("Label", secondary=submission_labels, backref="submissions")

    form = relationship("Form", back_populates="submissions")

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    display_name = Column(String)
    pfp_url = Column(String)
    disabled = Column(Boolean, nullable=False, default=False)
    settings = Column(JSON)
    custom = Column(JSON)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(JSON, nullable=False)

class Role(Base):
    __tablename__ = "roles"
    
    role_name = Column(String, primary_key=True)
    permissions = Column("permissions_json", JSON, nullable=False)

class PageMetric(Base):
    __tablename__ = "page_metrics"

    page_id = Column(ForeignKey("pages.id"), primary_key=True)
    key = Column(String, primary_key=True)   # "likes", "views", "shares"
    value = Column(Integer, nullable=False)

    __table_args__ = (
        Index("idx_metric_key_value", "key", "value"),
    )
