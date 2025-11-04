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
        tags TEXT, 
        thumb TEXT,
        type TEXT,
        created TEXT,
        updated TEXT,
        author TEXT,
        custom TEXT
    )
    ''')

    # Add missing columns for older databases
    for col, col_type in [
        ("created", "TEXT"),
        ("updated", "TEXT"),
        ("author", "TEXT"),
        ("custom", "TEXT"), 
    ]:
        try:
            conn.execute(f'ALTER TABLE pages ADD COLUMN {col} {col_type}')
        except sqlite3.OperationalError:
            pass  # Column already exists

    conn.commit()


def add_page(page: Page):
    """Add a new page to the database."""
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
    INSERT INTO pages (
        slug, title, content, markdown, html, tags, thumb, type, created, updated, author, custom
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        page.author if hasattr(page, 'author') else None,
        json.dumps(page.custom) if hasattr(page, 'custom') and page.custom else None  
    ))
    conn.commit()


def get_page(slug: str) -> Optional[Page]:
    """Get a page by its slug."""
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM pages WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    if row:
        # Note: Adjust indices if you add more columns later
        return Page(
            slug=row[0],
            title=row[1],
            content=row[2],
            markdown=row[3],
            html=row[4],
            tags=json.loads(row[5]) if row[5] else None,
            thumb=row[6],
            type=row[7],
            created=row[8],
            updated=row[9],
            author=row[10],
            custom=json.loads(row[11]) if len(row) > 11 and row[11] else {}  # 👈 NEW
        )
    return None


def update_page(page: Page):
    """Update an existing page."""
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
    UPDATE pages
    SET title = ?, content = ?, markdown = ?, html = ?, tags = ?, thumb = ?, type = ?, updated = ?, author = ?, custom = ?
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
        json.dumps(page.custom) if hasattr(page, 'custom') and page.custom else None,  # 👈 NEW
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
    cursor = conn.execute('''
        SELECT slug, title, content, markdown, html, tags, thumb, type, created, updated, author, custom
        FROM pages
    ''')
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
            created=row[8],
            updated=row[9],
            author=row[10],
            custom=json.loads(row[11]) if len(row) > 11 and row[11] else {}  # 👈 NEW
        )
        for row in rows
    ]


def close_connection():
    """Close the database connection."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None