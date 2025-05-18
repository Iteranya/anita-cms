import sqlite3
from typing import List, Optional
import json
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
        type TEXT
    )
    ''')
    conn.commit()

def add_page(page: Page):
    """Add a new page to the database."""
    conn = get_connection()
    conn.execute('''
    INSERT INTO pages (slug, title, content, markdown, html, tags, thumb, type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        page.slug,
        page.title,
        page.content,
        page.markdown,
        page.html,
        json.dumps(page.tags) if page.tags else None,
        page.thumb,
        page.type
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
            type=row[7]
        )
    return None

def update_page(page: Page):
    """Update an existing page."""
    conn = get_connection()
    conn.execute('''
    UPDATE pages
    SET title = ?, content = ?, markdown = ?, html = ?, tags = ?, thumb = ?, type = ?
    WHERE slug = ?
    ''', (
        page.title,
        page.content,
        page.markdown,
        page.html,
        json.dumps(page.tags) if page.tags else None,
        page.thumb,
        page.type,
        page.slug
    ))
    conn.commit()

def delete_page(slug: str):
    """Delete a page by its slug."""
    conn = get_connection()
    conn.execute('DELETE FROM pages WHERE slug = ?', (slug,))
    conn.commit()

#TODO: Refactor this later, no need to fetch html and markdown everytime to save client memory
def list_pages() -> List[Page]: 
    """List all pages in the database."""
    conn = get_connection()
    cursor = conn.execute('SELECT slug, title, content, markdown, html, tags, thumb, type FROM pages')
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
            type=row[7]
        )
        for row in rows
    ]

def close_connection():
    """Close the database connection."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None