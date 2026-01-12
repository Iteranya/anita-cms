import shutil
import os
from sqlalchemy import create_engine, text
from data import models  # Importing to get the exact table name

def create_sanitized_backup(
    source_db: str = "anita.db", 
    backup_db: str = "anita_sanitized.db"
):
    """
    1. Copies the entire database file (preserving all tables/roles/schema).
    2. Connects to the backup.
    3. Deletes all rows from the User table.
    4. Vacuums the file to remove binary traces of the deleted data.
    """
    
    # 1. Copy the database file (Copy Paste)
    if os.path.exists(backup_db):
        os.remove(backup_db)
    
    print(f"Copying '{source_db}' to '{backup_db}'...")
    try:
        shutil.copy2(source_db, backup_db)
    except FileNotFoundError:
        print(f"Error: Source database '{source_db}' not found.")
        return

    # 2. Connect to the NEW backup database
    backup_url = f"sqlite:///{backup_db}"
    engine = create_engine(backup_url)

    # 3. Delete User Data & Vacuum
    # We use engine.connect() to execute raw SQL commands
    with engine.connect() as conn:
        print("Stripping user data...")
        
        # Dynamically get the table name from the model
        user_table = models.User.__tablename__
        
        # Delete all rows in the user table
        conn.execute(text(f"DELETE FROM {user_table}"))
        conn.commit()
        
        # Verify count (Optional, just for log)
        result = conn.execute(text(f"SELECT COUNT(*) FROM {user_table}"))
        count = result.scalar()
        print(f"User count in backup: {count} (Should be 0)")

    # 4. VACUUM to physically remove the deleted data from the file
    # Vacuum cannot run inside a transaction block, so we use a separate connection with autocommit
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        print("Vacuuming database (removing traces)...")
        conn.execute(text("VACUUM"))

    print(f"✓ Backup complete: {backup_db}")

if __name__ == "__main__":
    create_sanitized_backup()