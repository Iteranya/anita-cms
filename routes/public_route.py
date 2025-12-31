from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from data.database import get_db
from data import schemas
from services.pages import PageService

# --- Dependency Setup ---
def get_page_service(db: Session = Depends(get_db)) -> PageService:
    return PageService(db)

router = APIRouter(tags=["Public"])

# ==========================================
# 🖼️ HTML SERVING ROUTES
# ==========================================

# TODO: Add slowapi for rate limit (not everyone set this up in Caddy/Nginx)

@router.get("/", response_class=HTMLResponse)
def serve_home_page(page_service: PageService = Depends(get_page_service)):
    """Serves the page labelged as 'home'."""
    page = page_service.get_first_page_by_labels(['sys:home','any:read'])
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Critical: Home page not configured, notify site owner.")

    # We serve the pre-rendered HTML directly from the database
    return HTMLResponse(content=page.html, status_code=200)

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
    if not page.labels or not {'sys:head', 'any:read'}.issubset(label.name for label in page.labels):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found in this category.")
    return page

@router.get("/api/{main}/{slug}", response_model=schemas.Page)
def api_get_any_page(main:str, slug: str, page_service: PageService = Depends(get_page_service)):
    """
    API endpoint to get a single public page by its slug.
    """
    page = page_service.get_page_by_slug(slug)
    
    if not page.labels or not {f'main:{main}', 'any:read'}.issubset(label.name for label in page.labels):
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found in this category.")

    return page

@router.get("/search", response_model=list[schemas.PageData])
def api_search_pages_by_labels(
    # Changed "..." to "None" to make it optional
    labels: Optional[List[str]] = Query(None, description="List of labels to filter pages by"),
    page_service: PageService = Depends(get_page_service),
):
    """
    Search pages by labels.
    All provided labels must be present on the page.
    If no labels are provided, returns all pages with 'any:read'.
    """
    # Initialize as empty list if no labels were provided to prevent crashing on .append()
    search_labels = labels if labels is not None else []
    print(search_labels)
    search_labels.append("any:read")
    
    pages = page_service.get_pages_by_labels(search_labels)

    return pages

# ==========================================
# 🚀 DYNAMIC ROUTES
# ==========================================

@router.get("/{slug}", response_class=HTMLResponse)
def serve_top_level_page(
    slug: str,
    page_service: PageService = Depends(get_page_service),
):
    page = page_service.get_page_by_slug(slug)

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    label_names = {label.name for label in page.labels}

    required_labels = {"sys:head", "any:read"}

    if not required_labels.issubset(label_names):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    return HTMLResponse(content=page.html, status_code=200)

    
@router.get("/{main}/{slug}", response_class=HTMLResponse)
def serve_any_post(slug: str, main:str,page_service: PageService = Depends(get_page_service)):
    """Serves a single page."""
    if main == slug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found.")
    page = page_service.get_page_by_slug(slug) # Service handles 404 if slug doesn't exist
    markdown_template = page_service.get_first_page_by_labels(['sys:template','any:read'])
    if not page.labels or not {f'main:{main}', 'any:read'}.issubset(label.name for label in page.labels):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found.")
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)
    else: # Patch, markdown_template will retrieve page from client side, will fix later
        return HTMLResponse(content=markdown_template.html, status_code=200)