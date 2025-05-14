import sqlite3
from dataclasses import dataclass, asdict
from typing import List, Optional
import json
import os
from data.models import Page

DB_PATH = "pages.db"


class PageDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()
        

    def _create_table(self):
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            slug TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            markdown TEXT,
            html TEXT,
            tags TEXT, -- Stored as JSON string
            thumb TEXT
        )
        ''')
        self.conn.commit()

    def add_page(self, page: Page):
        self.conn.execute('''
        INSERT INTO pages (slug, title, content, markdown, html, tags, thumb)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            page.slug,
            page.title,
            page.content,
            page.markdown,
            page.html,
            json.dumps(page.tags) if page.tags else None,
            page.thumb
        ))
        self.conn.commit()

    def get_page(self, slug: str) -> Optional[Page]:
        cursor = self.conn.execute('SELECT * FROM pages WHERE slug = ?', (slug,))
        row = cursor.fetchone()
        if row:
            return Page(
                slug=row[0],
                title=row[1],
                content=row[2],
                markdown=row[3],
                html=row[4],
                tags=json.loads(row[5]) if row[5] else None,
                thumb=row[6]
            )
        return None

    def update_page(self, page: Page):
        self.conn.execute('''
        UPDATE pages
        SET title = ?, content = ?, markdown = ?, html = ?, tags = ?, thumb = ?
        WHERE slug = ?
        ''', (
            page.title,
            page.content,
            page.markdown,
            page.html,
            json.dumps(page.tags) if page.tags else None,
            page.thumb,
            page.slug
        ))
        self.conn.commit()

    def delete_page(self, slug: str):
        self.conn.execute('DELETE FROM pages WHERE slug = ?', (slug,))
        self.conn.commit()

    def list_pages(self) -> List[Page]:
        cursor = self.conn.execute('SELECT * FROM pages')
        rows = cursor.fetchall()
        return [
            Page(
                slug=row[0],
                title=row[1],
                content=row[2],
                markdown=row[3],
                html=row[4],
                tags=json.loads(row[5]) if row[5] else None,
                thumb=row[6]
            )
            for row in rows
        ]

    def close(self):
        self.conn.close()
