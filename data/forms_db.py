import sqlite3
import json
from datetime import datetime
from typing import Optional, List
from data.models import Form

DB_PATH = "forms.db"
_connection = None

def get_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        create_tables()
    return _connection

def create_tables():
    conn = get_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS forms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        schema_json TEXT NOT NULL,
        created TEXT,
        updated TEXT
    )
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        form_slug TEXT NOT NULL,
        submission_json TEXT NOT NULL,
        created TEXT,
        FOREIGN KEY(form_slug) REFERENCES forms(slug)
    )
    ''')
    conn.commit()

# ----- Forms -----
def add_form(slug: str, title: str, schema: dict):
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
    INSERT INTO forms (slug, title, schema_json, created, updated)
    VALUES (?, ?, ?, ?, ?)
    ''', (slug, title, json.dumps(schema), now, now))
    conn.commit()

def get_form(slug: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute('SELECT * FROM forms WHERE slug = ?', (slug,)).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "slug": row[1],
        "title": row[2],
        "schema": json.loads(row[3]),
        "created": row[4],
        "updated": row[5]
    }

def list_forms() -> List[dict]:
    conn = get_connection()
    rows = conn.execute('SELECT * FROM forms').fetchall()
    return [
        {
            "id": r[0],
            "slug": r[1],
            "title": r[2],
            "schema": json.loads(r[3]),
            "created": r[4],
            "updated": r[5]
        }
        for r in rows
    ]

# ----- Submissions -----
def add_submission(form_slug: str, data: dict):
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
    INSERT INTO submissions (form_slug, submission_json, created)
    VALUES (?, ?, ?)
    ''', (form_slug, json.dumps(data), now))
    conn.commit()

def list_submissions(form_slug: str) -> List[dict]:
    conn = get_connection()
    rows = conn.execute('''
        SELECT id, form_slug, submission_json, created
        FROM submissions WHERE form_slug = ?
    ''', (form_slug,)).fetchall()
    return [
        {
            "id": r[0],
            "form_slug": r[1],
            "data": json.loads(r[2]),
            "created": r[3]
        }
        for r in rows
    ]

def update_form(form: Form):
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
        UPDATE forms
        SET title = ?, schema_json = ?, description = ?, updated = ?, author = ?, custom = ?
        WHERE slug = ?
    ''', (
        form.title,
        json.dumps(form.schema),
        getattr(form, "description", None),
        now,
        getattr(form, "author", None),
        json.dumps(getattr(form, "custom", {})),
        form.slug
    ))
    conn.commit()

def delete_form(slug: str):
    conn = get_connection()
    conn.execute('DELETE FROM forms WHERE slug = ?', (slug,))
    conn.commit()

def get_submission(submission_id: int) -> Optional[dict]:
    """Fetch a single submission by ID."""
    conn = get_connection()
    row = conn.execute('''
        SELECT id, form_slug, submission_json, created
        FROM submissions WHERE id = ?
    ''', (submission_id,)).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "form_slug": row[1],
        "data": json.loads(row[2]),
        "created": row[3]
    }


def update_submission(submission):
    """Update an existing submission."""
    conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute('''
        UPDATE submissions
        SET submission_json = ?, created = ?, author = ?, custom = ?
        WHERE id = ?
    ''', (
        json.dumps(submission.data),
        now,
        getattr(submission, "author", None),
        json.dumps(getattr(submission, "custom", {})),
        submission.id
    ))
    conn.commit()

def delete_submission(submission_id: int):
    """Delete a submission by its ID."""
    conn = get_connection()
    conn.execute('DELETE FROM submissions WHERE id = ?', (submission_id,))
    conn.commit()


def close_connection():
    global _connection
    if _connection:
        _connection.close()
        _connection = None
