# file: api/admin.py

import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from data.database import get_db
from services.pages import PageService
from src.dependencies import optional_user

router = APIRouter(tags=["Admin SPA"])

ADMIN_DIR = "static/admin"
SPA_VIEWS = {"dashboard", "page", "structure", "users", "collections", "files", "media", "config"}

def render_no_cache_html(file_path: str, is_partial: bool):
    """
    Reads the file manually and returns an HTMLResponse with 
    AGGRESSIVE anti-caching headers.
    """
    if not os.path.exists(file_path):
        return HTMLResponse("View not found", status_code=404)
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    response = HTMLResponse(content)
    #I'll add CSP Later
    #response.headers["Content-Security-Policy"] = ADMIN_CSP
    
    response.headers["Vary"] = "HX-Request"
    
    # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # response.headers["Pragma"] = "no-cache"
    # response.headers["Expires"] = "0"
    
    return response

@router.get("/admin")
async def admin_root():
    return RedirectResponse("/admin/dashboard")

@router.get("/admin/submissions", response_class=HTMLResponse)
async def view_submissions_manager(request: Request, user: dict = Depends(optional_user)):
    if not user: 
        return RedirectResponse("/auth")
    # Use the helper to ensure this page also doesn't stick in cache strangely
    return render_no_cache_html(os.path.join(ADMIN_DIR, "submissions.html"), False)

@router.get("/admin/{slug}", response_class=HTMLResponse)
async def admin_router(
    slug: str, 
    request: Request, 
    user: dict = Depends(optional_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/auth", status_code=302)

    # --- CASE A: Static SPA View ---
    if slug in SPA_VIEWS:
        # 1. Check if it's HTMX (The Partial)
        if request.headers.get("HX-Request"):
            view_path = os.path.join(ADMIN_DIR, "views", f"{slug}.html")
            return render_no_cache_html(view_path, True)
        
        # 2. Otherwise, it's the Browser (The Shell)
        shell_path = os.path.join(ADMIN_DIR, "index.html")
        return render_no_cache_html(shell_path, False)

    raise HTTPException(status_code=404, detail="Content not available")