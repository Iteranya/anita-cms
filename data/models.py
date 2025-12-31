# file: data/models.py

from sqlalchemy import Column, Index, Integer, String, Text, JSON, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from .database import Base

# --- ASSOCIATION TABLES ---

page_tags = Table(
    'page_tags', Base.metadata,
    Column('page_slug', String, ForeignKey('pages.slug'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

collection_tags = Table(
    'collection_tags', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

submission_tags = Table(
    'submission_tags', Base.metadata,
    Column('submission_id', Integer, ForeignKey('submissions.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


page_labels = Table(
    'page_labels', Base.metadata,
    Column('page_slug', String, ForeignKey('pages.slug'), primary_key=True),
    Column('label_id', Integer, ForeignKey('labels.id'), primary_key=True)
)

collection_labels = Table(
    'collection_labels', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id'), primary_key=True),
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

class Tag(Base):
    __tablename__ = 'tags'
    
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
    tags = relationship("Tag", secondary=page_tags, backref="pages")
    thumb = Column(String)
    type = Column(String)
    created = Column(String)
    updated = Column(String)
    author = Column(String)
    custom = Column(JSON)

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    schema = Column("schema_json", JSON, nullable=False)
    description = Column(Text)
    created = Column(String)
    updated = Column(String)
    author = Column(String)
    labels = relationship("Label", secondary=collection_labels, backref="collections")
    tags = relationship("Tag", secondary=collection_tags, backref="collections")
    
    custom = Column(JSON)
    submissions = relationship("Submission", back_populates="collection", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_slug = Column(String, ForeignKey("collections.slug", ondelete="CASCADE"), nullable=False)
    data = Column("submission_json", JSON, nullable=False)
    created = Column(String)
    updated = Column(String)
    author = Column(String)
    custom = Column(JSON)
    labels = relationship("Label", secondary=submission_labels, backref="submissions")
    tags = relationship("Tag", secondary=submission_tags, backref="submissions")
    collection = relationship("Collection", back_populates="submissions")

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
