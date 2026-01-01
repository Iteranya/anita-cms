# file: data/database.py

from sqlalchemy import create_engine, event  # <--- 1. Import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///anita.db"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# <--- 2. Add this block to toggle WAL mode
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
# --------------------------------------------

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_all_tables():
    """Create all tables in the database based on the SQLAlchemy models."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()