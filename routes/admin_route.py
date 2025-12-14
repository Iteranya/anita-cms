# file: api/admin.py

import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

# Local imports from our new architecture
from data.database import get_db
from services.pages import PageService

# Import the new, decoupled authentication dependencies
from src.dependencies import optional_user, require_admin

router = APIRouter(tags=["Admin Views (MPA)"])

ADMIN_APP_DIR = "static/admin"

def is_tag_in_db_page(db_page_tags: List, tag_name: str) -> bool:
    """
    Checks if a tag exists in a list of SQLALCHEMY OBJECTS.
    Used when inspecting existing data from the database.
    """
    if not db_page_tags:
        return False
    # Checks t.name because these are DB objects
    return any(t.name == tag_name for t in db_page_tags)

# --- HTML VIEW ROUTES (The Unified Dashboard - MPA Style) ---
#

@router.get("/admin", response_class=FileResponse)
async def view_dashboard(user: dict = Depends(optional_user)):
    """Main Dashboard. Accessible by ANY logged-in user."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Serves the static HTML file for the dashboard.
    return FileResponse(os.path.join(ADMIN_APP_DIR, "page_hikarin.html"))

@router.get("/admin/page", response_class=FileResponse)
async def view_page_manager(user: dict = Depends(optional_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return FileResponse(os.path.join(ADMIN_APP_DIR, "page_hikarin.html"))

@router.get("/admin/config", response_class=FileResponse)
async def view_config(user: dict = Depends(optional_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return FileResponse(os.path.join(ADMIN_APP_DIR, "config.html"))

@router.get("/admin/forms", response_class=FileResponse)
async def view_forms(user: dict = Depends(optional_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return FileResponse(os.path.join(ADMIN_APP_DIR, "form.html"))

@router.get("/admin/media", response_class=FileResponse)
async def view_media(user: dict = Depends(optional_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return FileResponse(os.path.join(ADMIN_APP_DIR, "media.html"))

@router.get("/admin/files", response_class=FileResponse)
async def view_files(user: dict = Depends(optional_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return FileResponse(os.path.join(ADMIN_APP_DIR, "file_manager.html"))

@router.get("/admin/users", response_class=FileResponse)
async def view_users(user: dict = Depends(optional_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return FileResponse(os.path.join(ADMIN_APP_DIR, "users_hikarin.html"))

# --- CUSTOM DYNAMIC ADMIN PAGES (from Database) ---

@router.get("/admin/{slug}", response_class=HTMLResponse)
async def serve_custom_admin_page(
    slug: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """
    Fetches a CMS page tagged with 'admin' and directly serves its raw HTML content.
    """
    page_service = PageService(db)
    # The service will raise a 404 if the page is not found
    page = page_service.get_page_by_slug(slug)

    # Check for the 'admin' tag
    if is_tag_in_db_page(page.tags,"sys:admin"):
        raise HTTPException(status_code=404, detail="Admin tool not found")

    # Check if the page is of type 'html' and has content
    if page.type == 'html' and page.html:
        return HTMLResponse(content=page.html, status_code=200)

    # If it's not a valid HTML admin page, it's not found in this context
    raise HTTPException(
        status_code=404,
        detail="Admin tool page is not configured for direct HTML display."
    )