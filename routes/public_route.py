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

# --- Helper for Authorization ---
def check_page_is_public(page: schemas.Page):
    """
    Raises a 404 error if the page is private.
    We use 404 instead of 403 to avoid revealing the existence of private content.
    """
    if not page.tags and "public" not in page.tags:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

# ==========================================
# 🖼️ HTML SERVING ROUTES
# ==========================================

@router.get("/", response_class=HTMLResponse)
def serve_home_page(page_service: PageService = Depends(get_page_service)):
    """Serves the page tagged as 'home'."""
    page = page_service.get_first_page_by_tag('home')
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Critical: Home page not configured, notify site owner.")

    # We serve the pre-rendered HTML directly from the database
    return HTMLResponse(content=page.html, status_code=200)


@router.get("/blog", response_class=HTMLResponse)
def serve_blog_index(page_service: PageService = Depends(get_page_service)):
    """Serves the page tagged as 'blog-home' as the main blog index."""
    page = page_service.get_first_page_by_tag('sys:blog-home')
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Critical: Blog index page not found, notify site owner")

    check_page_is_public(page)
    return HTMLResponse(content=page.html, status_code=200)


@router.get("/blog/{slug}", response_class=HTMLResponse)
def serve_blog_post(slug: str, page_service: PageService = Depends(get_page_service)):
    """Serves a single blog post page."""
    page = page_service.get_page_by_slug(slug) # Service handles 404 if slug doesn't exist
    markdown_template = page_service.get_first_page_by_tag('sys:blog-template')
    
    # Ensure this endpoint only serves pages with the 'sys:blog' tag
    if not page.tags or ('sys:blog' not in page.tags or 'sys:public' not in page.tags):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found.")
        
    check_page_is_public(page)
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)
    else:
        return HTMLResponse(content=markdown_template.html, status_code=200)


# ==========================================
# 🚀 PUBLIC API ROUTES
# ==========================================


@router.get("/api/blog", response_model=List[schemas.Page])
def api_list_blog_pages(page_service: PageService = Depends(get_page_service)):
    """
    API endpoint to get a list of all pages tagged with both 'sys:blog' and 'sys:public'.
    The response is automatically serialized by FastAPI based on the Pydantic schema.
    """
    # 1. Fetch all pages that have the 'sys:blog' tag
    all_blog_pages = page_service.get_pages_by_tag("sys:blog")
    
    # 2. Filter that list to only include pages that also have the 'sys:public' tag
    public_blog_pages = [
        page for page in all_blog_pages if "sys:public" in page.tags
    ]
    
    return public_blog_pages


@router.get("/api/blog/{slug}", response_model=schemas.Page)
def api_get_blog_page(slug: str, page_service: PageService = Depends(get_page_service)):
    """
    API endpoint to get a single public blog page by its slug.
    """
    page = page_service.get_page_by_slug(slug)
    
    if not page.tags or "sys:blog" not in page.tags:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found in this category.")

    check_page_is_public(page)
    return page

@router.get("/{slug}", response_class=HTMLResponse)
def serve_generic_page(slug: str, page_service: PageService = Depends(get_page_service)):
    """
    Serves a generic top-level page by its slug.
    This acts as a catch-all for any slug not matched by other routes.
    """
    page = page_service.get_page_by_slug(slug)
    check_page_is_public(page)
    if not page.tags or 'main' not in page.tags:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found in this category.")
    return HTMLResponse(content=page.html, status_code=200)
