from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List, Optional
from sqlalchemy.orm import Session
from data.database import get_db
from data import schemas
from services.pages import PageService
from src.dependencies import get_current_user, optional_user as optional_auth
from data.models import User as CurrentUser

# --- Dependency Setup ---
# This dependency provider makes the PageService available to our routes
def get_page_service(db: Session = Depends(get_db)) -> PageService:
    return PageService(db)

# --- Router Definition ---
router = APIRouter(prefix="/pages", tags=["Pages"])


# ----------------------------------------------------
# 📄 PAGES CRUD
# ----------------------------------------------------

@router.post("/", response_model=schemas.Page, status_code=status.HTTP_201_CREATED)
def create_page(
    page_in: schemas.PageCreate,
    page_service: PageService = Depends(get_page_service),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Create a new page. The author is automatically set to the current user.
    The service layer will handle slug uniqueness and other business rules.
    """
    # Assign the current user as the author before creation
    page_in.author = user.username
    
    return page_service.create_new_page(page_data=page_in)


@router.get("/", response_model=List[schemas.Page])
def list_pages(
    skip: int = 0,
    limit: int = 100,
    page_service: PageService = Depends(get_page_service),
    user: Optional[CurrentUser] = Depends(optional_auth),
):
    """
    List all pages.
    - If a user is not authenticated, only public pages (without a 'private' tag) are returned.
    - If a user is authenticated, all pages are returned.
    """
    all_pages = page_service.get_all_pages(skip=skip, limit=limit)
    
    # Authorization Logic: Filter out private pages for anonymous users
    if not user:
        return [page for page in all_pages if not (page.tags and "private" in page.tags)]
        
    return all_pages


@router.get("/{slug}", response_model=schemas.Page)
def get_page(
    slug: str,
    page_service: PageService = Depends(get_page_service),
    user: Optional[CurrentUser] = Depends(optional_auth),
):
    """
    Get a single page by its unique slug.
    If the page is tagged as 'private', an authenticated user is required.
    """
    page = page_service.get_page_by_slug(slug)
    
    # Authorization Logic: Protect private pages
    is_private = page.tags and "private" in page.tags
    if is_private and not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to view this page."
        )
        
    return page


@router.put("/{slug}", response_model=schemas.Page)
def update_page(
    slug: str,
    page_update: schemas.PageUpdate,
    page_service: PageService = Depends(get_page_service),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Update an existing page.
    Only the original author of the page can update it.
    """
    # First, get the page to check for authorship
    db_page = page_service.get_page_by_slug(slug)
    
    # Authorization Logic: Only the author can update
    if db_page.author != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this page."
        )
        
    return page_service.update_existing_page(slug=slug, page_update_data=page_update)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(
    slug: str,
    page_service: PageService = Depends(get_page_service),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Delete a page by its slug.
    Only the original author of the page can delete it.
    """
    # First, get the page to check for authorship before deleting
    db_page = page_service.get_page_by_slug(slug)
    
    # Authorization Logic: Only the author can delete
    if db_page.author != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this page."
        )
        
    page_service.delete_page_by_slug(slug)
    
    # Return a 204 response which has no content body
    return Response(status_code=status.HTTP_204_NO_CONTENT)