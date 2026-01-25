# file: api/admin.py

import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from data.database import get_db
from routes.public_route import render_db_template
from services.pages import PageService
from src.dependencies import optional_user

router = APIRouter(tags=["Admin SPA"])
def get_page_service(db: Session = Depends(get_db)) -> PageService:
    return PageService(db)

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

@router.get("/admin/preview/{slug}", response_class=HTMLResponse)
def serve_any_post(slug: str, page_service: PageService = Depends(get_page_service)):
    """
    Serves a single page with SSR.
    1. Fetches the content page.
    2. Fetches the layout template.
    3. Renders the template with content injected before sending to client.
    """
    
    # 1. Fetch the actual content page
    page = page_service.get_page_by_slug(slug) 

    # 2. If it's already static HTML, return it
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)

    # 3. Handle Markdown/Dynamic Pages (SSR)
    # Fetch the template
    markdown_template = page_service.get_first_page_by_labels(['sys:template', 'any:read'])
    if not markdown_template:
        raise HTTPException(status_code=500, detail="System Error: Markdown template missing.")
    
    context = {
        "title": page.title,
        "markdown_content": page.markdown,
        "author": page.author if hasattr(page, 'author') else "Unknown",
        "published": page.created if hasattr(page, 'created_at') else "",
        "updated": page.updated if hasattr(page, 'updated_at') else "",
        "description": page.content if hasattr(page, 'description') else "",
        "thumb": page.thumb if hasattr(page, 'thumbnail') else ""
    }

    # Render on Server
    rendered_html = render_db_template(markdown_template.html, context)
    
    return HTMLResponse(content=rendered_html, status_code=200)