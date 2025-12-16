from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List, Optional
from sqlalchemy.orm import Session

from data.database import get_db
from data import schemas
from data.schemas import CurrentUser, Page
from services.pages import PageService
from services.users import UserService
from src import dependencies as dep
from src.audit import logger

# --- Dependency Setup ---

def get_page_service(db: Session = Depends(get_db)) -> PageService:
    return PageService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# --- Helper Logic ---

def is_tag_in_db_page(db_page_tags: List, tag_name: str) -> bool:
    """
    Checks if a tag exists in a list of SQLALCHEMY OBJECTS.
    Used when inspecting existing data from the database.
    """
    if not db_page_tags:
        return False
    # Checks t.name because these are DB objects
    return any(t.name == tag_name for t in db_page_tags)

def ensure_tag_in_schema(tags_list: List[str], tag_name: str) -> List[str]:
    """
    Ensures a tag string exists in a list of STRINGS.
    Used when manipulating Pydantic input schemas (PageCreate/Update).
    """
    if tags_list is None:
        tags_list = []
    
    if tag_name not in tags_list:
        tags_list.append(tag_name)
    
    return tags_list

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
    permissions = user_service.get_user_permissions(user.username)
    
    can_create_any = "*" in permissions or "page:create" in permissions
    can_create_blog = "blog:create" in permissions

    if can_create_any:
        # User is admin or page creator, no modification needed
        pass
    elif can_create_blog:
        # Restricted Blog Creator:
        # 1. Force type to markdown
        page_in.type = "markdown"
        # 2. Force 'sys:blog' tag (Input is List[str], so we append string)
        page_in.tags = ensure_tag_in_schema(page_in.tags, "sys:blog")
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a page."
        )

    page_in.author = user.username
    logger.info(f"{user.username} created page: {page_in.slug}")
    return page_service.create_new_page(page_data=page_in)


@router.get("/list", response_model=List[Page])
def list_pages(
    skip: int = 0,
    limit: int = 100,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service),
    user: Optional[CurrentUser] = Depends(dep.optional_user),
):
    """
    Lists pages. Pushes filtering to the service layer.
    """
    permissions = set()
    if user:
        permissions = set(user_service.get_user_permissions(user.username))

    # 1. Admin / Full Read
    if "*" in permissions or "page:read" in permissions:
        return page_service.get_all_pages(skip=skip, limit=limit)
    
    # 2. Blog Reader
    if "blog:read" in permissions:
        # Filter by string tags
        return page_service.get_pages_by_tags(
            tags=["sys:blog", "sys:public"], 
            skip=skip, 
            limit=limit
        )

    # 3. Public / Anonymous
    return page_service.get_pages_by_tag(
        tag="sys:public", 
        skip=skip, 
        limit=limit
    )


@router.get("/{slug}", response_model=schemas.Page)
def get_page(
    slug: str,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service),
    user: Optional[CurrentUser] = Depends(dep.optional_user),
):
    # Returns DB Object (with tag objects)
    page = page_service.get_page_by_slug(slug)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    # 1. Check Public Access (using helper for DB objects)
    if is_tag_in_db_page(page.tags, "sys:public"):
        return page

    # 2. Authentication Required
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    permissions = set(user_service.get_user_permissions(user.username))

    # 3. Check Permissions
    can_read_all = "*" in permissions or "page:read" in permissions
    # Check if page has sys:blog tag (checking DB objects)
    is_blog_page = is_tag_in_db_page(page.tags, "sys:blog")
    can_read_blog = "blog:read" in permissions and is_blog_page

    if can_read_all or can_read_blog:
        return page

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.put("/{slug}", response_model=schemas.Page)
def update_page(
    slug: str,
    page_update: schemas.PageUpdate,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service),
    user: CurrentUser = Depends(dep.get_current_user),
):
    db_page = page_service.get_page_by_slug(slug)
    if not db_page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")

    permissions = set(user_service.get_user_permissions(user.username))

    
    # Check for a "master" permission that allows managing any page.
    has_master_permission = "*" in permissions or "page:update" in permissions

    # If the user is trying to update tags AND they lack the master permission...
    if page_update.tags is not None and not has_master_permission:
        
        # 1. Preserve existing protected tags from the database object.
        preserved_system_tags = [
            tag.name for tag in db_page.tags if tag.name.startswith("sys:")
        ]
        
        # 2. Filter the user's input to get only the descriptive tags.
        new_descriptive_tags = [
            tag for tag in page_update.tags if not tag.startswith("sys:")
        ]
        
        # 3. Overwrite the user's tag list with the safe, merged list.
        page_update.tags = preserved_system_tags + new_descriptive_tags
    
    is_blog_page = is_tag_in_db_page(db_page.tags, "sys:blog")
    is_author = db_page.author == user.username
    has_blog_rights = is_blog_page and ("blog:update" in permissions or is_author)

    if not (has_master_permission or has_blog_rights):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    logger.info(f"User '{user.username}' updating page '{slug}'")
    return page_service.update_existing_page(slug=slug, page_update_data=page_update)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(
    slug: str,
    page_service: PageService = Depends(get_page_service),
    user_service: UserService = Depends(get_user_service), 
    user: CurrentUser = Depends(dep.get_current_user),
):
    db_page = page_service.get_page_by_slug(slug)
    if not db_page:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    permissions = set(user_service.get_user_permissions(user.username))
    
    is_author = db_page.author == user.username
    is_admin = "*" in permissions or "page:delete" in permissions
    
    is_blog_page = is_tag_in_db_page(db_page.tags, "sys:blog")
    can_delete_blog = "blog:delete" in permissions and is_blog_page

    if is_author or is_admin or can_delete_blog:
        logger.info(f"{user.username} deleted page: {slug}")
        page_service.delete_page_by_slug(slug)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")