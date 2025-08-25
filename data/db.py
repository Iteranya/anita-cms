import sqlite3
from typing import List, Optional
import json
from datetime import datetime
from data.models import Page

DB_PATH = "pages.db"
_connection = None

def get_connection():
    """Get a database connection, creating it if needed."""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        create_table()
    return _connection

def create_table():
    """Create the pages table if it doesn't exist."""
    conn = get_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        slug TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        markdown TEXT,
        html TEXT,
        tags TEXT, -- Stored as JSON string
        thumb TEXT,
        type TEXT,
        created TEXT,
        updated TEXT,
        author TEXT
    )
    ''')
    
    # Add new columns if they don't exist (for existing databases)
    try:
        conn.execute('ALTER TABLE pages ADD COLUMN created TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        conn.execute('ALTER TABLE pages ADD COLUMN updated TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        conn.execute('ALTER TABLE pages ADD COLUMN author TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()

def add_page(page: Page):
    """Add a new page to the database."""
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
    INSERT INTO pages (slug, title, content, markdown, html, tags, thumb, type, created, updated, author)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        page.slug,
        page.title,
        page.content,
        page.markdown,
        page.html,
        json.dumps(page.tags) if page.tags else None,
        page.thumb,
        page.type,
        page.created if hasattr(page, 'created') and page.created else now,
        page.updated if hasattr(page, 'updated') and page.updated else now,
        page.author if hasattr(page, 'author') else None
    ))
    conn.commit()

def get_page(slug: str) -> Optional[Page]:
    """Get a page by its slug."""
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM pages WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    if row:
        return Page(
            slug=row[0],
            title=row[1],
            content=row[2],
            markdown=row[3],
            html=row[4],
            tags=json.loads(row[5]) if row[5] else None,
            thumb=row[6],
            type=row[7],
            created=row[8] if len(row) > 8 else None,
            updated=row[9] if len(row) > 9 else None,
            author=row[10] if len(row) > 10 else None
        )
    return None

def update_page(page: Page):
    """Update an existing page."""
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
    UPDATE pages
    SET title = ?, content = ?, markdown = ?, html = ?, tags = ?, thumb = ?, type = ?, updated = ?, author = ?
    WHERE slug = ?
    ''', (
        page.title,
        page.content,
        page.markdown,
        page.html,
        json.dumps(page.tags) if page.tags else None,
        page.thumb,
        page.type,
        page.updated if hasattr(page, 'updated') and page.updated else now,
        page.author if hasattr(page, 'author') else None,
        page.slug
    ))
    conn.commit()

def delete_page(slug: str):
    """Delete a page by its slug."""
    conn = get_connection()
    conn.execute('DELETE FROM pages WHERE slug = ?', (slug,))
    conn.commit()


def list_pages() -> List[Page]: 
    """List all pages in the database."""
    conn = get_connection()
    cursor = conn.execute('SELECT slug, title, content, markdown, html, tags, thumb, type, created, updated, author FROM pages')
    rows = cursor.fetchall()
    return [
        Page(
            slug=row[0],
            title=row[1],
            content=row[2],
            markdown=row[3],
            html=row[4],
            tags=json.loads(row[5]) if row[5] else None,
            thumb=row[6],
            type=row[7],
            created=row[8] if len(row) > 8 else None,
            updated=row[9] if len(row) > 9 else None,
            author=row[10] if len(row) > 10 else None
        )
        for row in rows
    ]

def close_connection():
    """Close the database connection."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None