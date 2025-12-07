# file: data/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///anita.db"

# Create the SQLAlchemy engine
# connect_args is needed for SQLite to allow multi-threaded access, common in web apps.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal will be the session class for our database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base will be used as a base class for our ORM models in models.py
Base = declarative_base()

def create_all_tables():
    """Create all tables in the database based on the SQLAlchemy models."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created.")

# Dependency for getting a DB session (useful in web frameworks like FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()