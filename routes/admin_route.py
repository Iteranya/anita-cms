# file: api/admin.py

import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

# Local imports from our new architecture
from data.database import get_db
from services.pages import PageService

# Import the new, decoupled authentication dependencies
from src.dependencies import get_current_user, require_admin

router = APIRouter(tags=["Admin Views (MPA)"])

ADMIN_APP_DIR = "static/admin"

# --- HTML VIEW ROUTES (The Unified Dashboard - MPA Style) ---

@router.get("/admin", response_class=FileResponse)
async def view_dashboard(user: dict = Depends(get_current_user)):
    """Main Dashboard. Accessible by ANY logged-in user."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Serves the static HTML file for the dashboard.
    return FileResponse(os.path.join(ADMIN_APP_DIR, "page.html"))

@router.get("/admin/page", response_class=FileResponse)
async def view_page_manager(user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return FileResponse(os.path.join(ADMIN_APP_DIR, "page.html"))

@router.get("/admin/config", response_class=FileResponse)
async def view_config(user: dict = Depends(require_admin)):
    return FileResponse(os.path.join(ADMIN_APP_DIR, "config.html"))

@router.get("/admin/forms", response_class=FileResponse)
async def view_forms(user: dict = Depends(require_admin)):
    return FileResponse(os.path.join(ADMIN_APP_DIR, "form.html"))

@router.get("/admin/media", response_class=FileResponse)
async def view_media(user: dict = Depends(require_admin)):
    return FileResponse(os.path.join(ADMIN_APP_DIR, "media.html"))

@router.get("/admin/files", response_class=FileResponse)
async def view_files(user: dict = Depends(require_admin)):
    return FileResponse(os.path.join(ADMIN_APP_DIR, "file_manager.html"))

@router.get("/admin/users", response_class=FileResponse)
async def view_users(user: dict = Depends(require_admin)):
    return FileResponse(os.path.join(ADMIN_APP_DIR, "users.html"))

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
    if not page.tags or 'admin' not in page.tags:
        raise HTTPException(status_code=404, detail="Admin tool not found")

    # Check if the page is of type 'html' and has content
    if page.type == 'html' and page.html:
        return HTMLResponse(content=page.html, status_code=200)

    # If it's not a valid HTML admin page, it's not found in this context
    raise HTTPException(
        status_code=404,
        detail="Admin tool page is not configured for direct HTML display."
    )