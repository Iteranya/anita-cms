# file: api/admin.py

import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from data.database import get_db
from src.dependencies import optional_user

router = APIRouter(tags=["Admin SPA"])

AUTH_DIR = "static/auth"
SPA_VIEWS = {"login","setup","register"}

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
    
    response.headers["Vary"] = "HX-Request"

    return response

@router.get("/admin")
async def admin_root():
    return RedirectResponse("/admin/dashboard")

@router.get("/admin/submissions", response_class=HTMLResponse)
async def view_submissions_manager(request: Request, user: dict = Depends(optional_user)):
    if not user: 
        return RedirectResponse("/auth/login")
    # Use the helper to ensure this page also doesn't stick in cache strangely
    return render_no_cache_html(os.path.join(AUTH_DIR, "submissions.html"), False)

@router.get("/admin/{slug}", response_class=HTMLResponse)
async def admin_router(
    slug: str, 
    request: Request, 
    user: dict = Depends(optional_user),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # --- CASE A: Static SPA View ---
    if slug in SPA_VIEWS:
        # 1. Check if it's HTMX (The Partial)
        if request.headers.get("HX-Request"):
            view_path = os.path.join(AUTH_DIR, "views", f"{slug}.html")
            return render_no_cache_html(view_path, True)
        
        # 2. Otherwise, it's the Browser (The Shell)
        shell_path = os.path.join(AUTH_DIR, "index.html")
        return render_no_cache_html(shell_path, False)

    raise HTTPException(status_code=404, detail="Content not available")