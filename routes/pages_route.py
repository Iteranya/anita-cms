from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List, Optional
from sqlalchemy.orm import Session
from data.database import get_db
from data import schemas
from services.pages import PageService
from services.users import UserService
from src import dependencies as dep
from data.schemas import CurrentUser, Page
from src.audit import logger
# --- Dependency Setup ---
# This dependency provider makes the PageService available to our routes
def get_page_service(db: Session = Depends(get_db)) -> PageService:
    return PageService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get an instance of UserService with a DB session."""
    return UserService(db)

# --- Router Definition ---
router = APIRouter(prefix="/page", tags=["Pages"])


# ----------------------------------------------------
# 📄 PAGES CRUD
# ----------------------------------------------------

@router.post("/", response_model=schemas.Page, status_code=status.HTTP_201_CREATED)
def create_page(
    page_in: schemas.PageCreate,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(dep.get_current_user),  
):
    """
    Create a new page with permission-based restrictions.
    - Users with 'page:create' or admin rights can create any type of page.
    - Users with only 'blog:create' permission can create pages, but they
      MUST include the 'sys:blog' tag and are restricted to the 'markdown'
      page type.
    """
    user_permissions = user_service.get_user_permissions(user.username)

    can_create_any_page = "*" in user_permissions or "page:create" in user_permissions
    can_create_blog_page = "blog:create" in user_permissions

    if can_create_any_page:
        # User has full page creation privileges. No special checks needed.
        pass
    elif can_create_blog_page:
        # User only has permission to create blog posts. Enforce rules.

        # 1. Rule: Must include the 'sys:blog' tag.
        if "sys:blog" not in page_in.tags:
            page_in.tags.append("sys:blog")

        # 2. Rule: Page type is hardcoded to 'markdown'.
        page_in.type = "markdown"

    else:
        # User has neither of the required permissions.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a page."
        )
    page_in.author = user.username
    logger.info(f"{user.username} attempted to create the page: {page_in.slug}")
    return page_service.create_new_page(page_data=page_in)


@router.get("/list", response_model=List[Page])
def list_pages(
    skip: int = 0,
    limit: int = 100,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service),
    user: CurrentUser = Depends(dep.get_current_user),
):
    """
    List all pages with permission-based filtering.
    - Users with 'page:read' permission (or admin) can see all pages.
    - Users with only 'blog:read' permission can see pages tagged with 'sys:blog'.
    - Non Anonymous user without either permission can only see public page.
    - Anonymous users who never register will get an error
    """

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    user_permissions = user_service.get_user_permissions(user.username)

    if "*" in user_permissions or "page:read" in user_permissions:
        return page_service.get_all_pages(skip=skip, limit=limit)
    
    elif "blog:read" in user_permissions:
        blog_pages = page_service.get_pages_by_tag("sys:blog")
        return blog_pages[skip : skip + limit]

    else:
        public_pages = page_service.get_pages_by_tag("public")
        return public_pages[skip : skip + limit]

@router.get("/{slug}", response_model=schemas.Page)
def get_page(
    slug: str,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service),
    user: Optional[CurrentUser] = Depends(dep.optional_user),
):
    """
    Get a single page by its unique slug.
    Access is granted based on user permissions and page tags.
    """
    page = page_service.get_page_by_slug(slug)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    # If not public, a user must be authenticated
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required for this page")

    user_permissions = user_service.get_user_permissions(user.username)

    if "*" in user_permissions or "page:read" in user_permissions:
        return page
    elif "blog:read" in user_permissions and "sys:blog" in page.tags:
        return page
    else:
        # If user is authenticated but lacks specific permissions for this non-public page
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this page."
        )


@router.put("/{slug}", response_model=schemas.Page)
def update_page(
    slug: str,
    page_update: schemas.PageUpdate,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service),
    user: CurrentUser = Depends(dep.get_current_user),
):
    """
    Update an existing page using a hybrid permission model.

    This model provides tight security for critical system pages while offering
    a user-friendly ownership model for regular content (e.g., blogs).

    - **Full Privileges (System Pages & Overrides):**
      - Users with '*' or 'page:update' permissions can modify any page without
        restriction. This is intended for administrators managing system pages
        (e.g., 'home', 'about', templates).
      - For non-blog pages, these are the ONLY permissions that allow an update.

    - **Restricted Privileges (Blog Pages):**
      - For pages explicitly tagged with 'sys:blog', access is broader.
      - The original author OR a user with 'blog:update' can edit the page.
      - When editing under these restricted permissions, the following rules
        are enforced by the API to maintain integrity:
          1. The 'sys:blog' tag CANNOT be removed.
          2. The page 'type' (e.g., 'markdown') CANNOT be changed.
    """
    db_page = page_service.get_page_by_slug(slug)
    if not db_page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    user_permissions = user_service.get_user_permissions(user.username)

    # --- Define Permission Flags for Clarity ---

    is_author = db_page.author == user.username
    is_blog_page = "sys:blog" in db_page.tags

    # 1. Check for "overlord" permissions that grant unrestricted access to ANY page.
    has_full_privileges = (
        "*" in user_permissions
        or "page:update" in user_permissions
    )

    # 2. Check for the specific, more lenient permissions that apply ONLY to blog pages.
    can_update_blog_page = (
        is_blog_page
        and ("blog:update" in user_permissions or is_author)
    )

    # --- Authorization Check (Default Deny) ---
    # The user must meet one of the two criteria to be authorized.
    is_authorized = has_full_privileges or can_update_blog_page

    if not is_authorized:
        # If user has neither full privileges nor blog-specific permissions, deny access.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this page."
        )

    # --- Restriction Enforcement ---
    # If the user is authorized, we now check IF they are acting under the restricted
    # blog permissions. If so, we enforce the integrity rules.
    if not has_full_privileges:
        # This block only runs if the user is authorized *solely* because they
        # are a blog author or have the 'blog:update' permission.

        # Rule 1: Enforce that the page type cannot be changed.
        # We overwrite any incoming 'type' with the original to prevent modification.
        page_update.type = db_page.type

        # Rule 2: Enforce that the 'sys:blog' tag is not removed.
        # If an update to tags is provided and it's missing, we add it back.
        if page_update.tags is not None and "sys:blog" not in page_update.tags:
            page_update.tags.append("sys:blog")

    # --- Perform Update ---
    # If we've reached this point, the user is authorized and all necessary
    # restrictions have been applied to the update payload.
    logger.info(f"User '{user.username}' is updating page '{slug}'.")
    return page_service.update_existing_page(slug=slug, page_update_data=page_update)

@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(
    slug: str,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service), 
    user: CurrentUser = Depends(dep.get_current_user),
):
    """
    Delete a page by its slug.
    Permission is granted if the user is the author, an admin, has the 'page:delete'
    permission, or has the 'blog:delete' permission for a page tagged as 'sys:blog'.
    """
    db_page = page_service.get_page_by_slug(slug)
    if not db_page:
        # We still return 204 to avoid leaking information about which pages exist
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    user_permissions = user_service.get_user_permissions(user.username)
    
    # Authorization Logic: Check all allowed conditions
    is_author = db_page.author == user.username
    is_admin = "*" in user_permissions
    can_delete_all_pages = "page:delete" in user_permissions
    can_delete_blog_pages = ("blog:delete" in user_permissions and "sys:blog" in db_page.tags)

    if not (is_author or is_admin or can_delete_all_pages or can_delete_blog_pages):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this page."
        )
    
    logger.info(f"{user.username} attempted to delete the page: {slug}")
        
    page_service.delete_page_by_slug(slug)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)