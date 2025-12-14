# file: api/admin.py

import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from data.database import get_db
from services.pages import PageService
from src.dependencies import optional_user

router = APIRouter(tags=["Admin SPA"])

# 1. Configuration
ADMIN_DIR = "static/admin"
SPA_VIEWS = {"dashboard", "page", "users", "forms", "files", "media", "config"}

# 2. The Renderer (Internal Helper)
def render_spa_view(request: Request, view_name: str):
    """
    Decides whether to serve the Shell (index.html) or the Partial (views/*.html)
    based on the HTMX header.
    """
    # 1. HTMX Request -> Serve Partial
    if request.headers.get("HX-Request"):
        view_path = os.path.join(ADMIN_DIR, "views", f"{view_name}.html")
        if os.path.exists(view_path):
            res = FileResponse(view_path)
            # Crucial: Tell browser this URL's content varies based on headers
            res.headers["Vary"] = "HX-Request"
            res.headers["Cache-Control"] = "no-store, max-age=0"
            return res
        return HTMLResponse("<div class='p-8'>View not found</div>", status_code=404)
    
    # 2. Browser Request -> Serve Shell
    res = FileResponse(os.path.join(ADMIN_DIR, "index.html"))
    # FIX IS HERE: Disable caching for the shell too, so the browser 
    # doesn't assume this result is valid for the subsequent HTMX request.
    res.headers["Cache-Control"] = "no-store, max-age=0"
    res.headers["Vary"] = "HX-Request"
    return res

# 3. Routes

@router.get("/admin")
async def admin_root():
    return RedirectResponse("/admin/dashboard")

@router.get("/admin/{slug}", response_class=HTMLResponse)
async def admin_router(
    slug: str, 
    request: Request, 
    user: dict = Depends(optional_user),
    db: Session = Depends(get_db)
):
    """
    The Unified Admin Handler.
    Priority:
    1. Is it a Static Admin View (e.g. 'users', 'config')? -> Serve SPA
    2. Is it a Dynamic DB Page (e.g. 'custom-tool')? -> Serve HTML
    """
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # --- CASE A: Static SPA View (dashboard, users, etc) ---
    if slug in SPA_VIEWS:
        return render_spa_view(request, slug)

    # --- CASE B: Dynamic Database Page ---
    # If the slug isn't a known system view, check the database.
    # We require full admin privileges for dynamic tools.
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    page_service = PageService(db)
    page = page_service.get_page_by_slug(slug) # Raises 404 if not found

    # Logic Check: Ensure it is actually an admin tool
    # (Checking if ANY tag matches 'sys:admin')
    is_admin_tool = any(t.name == "sys:admin" for t in page.tags)
    
    if not is_admin_tool:
        raise HTTPException(status_code=404, detail="Page is not an admin tool")

    if page.type == 'html' and page.html:
        return HTMLResponse(content=page.html, status_code=200)

    raise HTTPException(status_code=404, detail="Content not available")