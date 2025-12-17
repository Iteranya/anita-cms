from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from data.database import get_db
from data import schemas
from services.pages import PageService

# --- Dependency Setup ---
def get_page_service(db: Session = Depends(get_db)) -> PageService:
    return PageService(db)

router = APIRouter(tags=["Public"])

# TODO: Database Optimization

# ==========================================
# 🖼️ HTML SERVING ROUTES
# ==========================================

@router.get("/", response_class=HTMLResponse)
def serve_home_page(page_service: PageService = Depends(get_page_service)):
    """Serves the page tagged as 'home'."""
    print("hello")
    page = page_service.get_first_page_by_tags(['sys:home','any:read'])
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Critical: Home page not configured, notify site owner.")

    # We serve the pre-rendered HTML directly from the database
    return HTMLResponse(content=page.html, status_code=200)


@router.get("/{slug}", response_class=HTMLResponse)
def serve_top_level_page(slug: str, page_service: PageService = Depends(get_page_service)):
    """Serves the top level page"""
    page = page_service.get_first_page_by_tags([f'main:{slug}','any:read'])
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    return HTMLResponse(content=page.html, status_code=200)
    
@router.get("/{main}/{slug}", response_class=HTMLResponse)
def serve_any_post(slug: str, main:str,page_service: PageService = Depends(get_page_service)):
    """Serves a single page."""
    page = page_service.get_page_by_slug(slug) # Service handles 404 if slug doesn't exist
    markdown_template = page_service.get_first_page_by_tags(['sys:template','any:read'])

    if not page.tags or not {f'main:{main}', 'any:read'}.issubset(tag.name for tag in page.tags):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found.")
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)
    else: # Patch, markdown_template will retrieve page from client side, will fix later
        return HTMLResponse(content=markdown_template.html, status_code=200)
    



# ==========================================
# 🚀 PUBLIC API ROUTES
# ==========================================

@router.get("/api/{slug}", response_class=schemas.Page)
def serve_generic_page(slug: str, page_service: PageService = Depends(get_page_service)):
    """
    Serves a generic top-level page by its slug.
    This acts as a catch-all for any slug not matched by other routes.
    """
    page = page_service.get_page_by_slug(slug)
    if not page.tags or not {f'main:{slug}', 'any:read'}.issubset(tag.name for tag in page.tags):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found in this category.")
    return page

@router.get("/api/{main}/{slug}", response_model=schemas.Page)
def api_get_any_page(main:str, slug: str, page_service: PageService = Depends(get_page_service)):
    """
    API endpoint to get a single public page by its slug.
    """
    page = page_service.get_page_by_slug(slug)
    
    if not page.tags or not {f'main:{main}', 'any:read'}.issubset(tag.name for tag in page.tags):
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found in this category.")

    return page