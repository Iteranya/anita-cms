# file: routers/dashboard.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Set

# Assuming your models and schemas are accessible
from data import schemas, models
from services.dashboard import DashboardService
from services.users import UserService
from src.dependencies import get_current_user, get_db

# --- Dependency Setup ---

def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# --- RBAC Helper for this Router ---

def _filter_page_list_for_user(pages: List[models.Page], permissions: Set[str]) -> List[models.Page]:
    """
    Filters a list of Page objects based on the user's permissions.
    This logic mirrors the filtering in the main /page/list endpoint.
    """
    # Admins or users with full page:read permission see everything.
    if "*" in permissions or "page:read" in permissions:
        return pages

    can_read_blog = "blog:read" in permissions
    
    filtered_pages = []
    for page in pages:
        is_public = any(tag.name == 'sys:public' for tag in page.tags)
        is_blog = any(tag.name == 'sys:blog' for tag in page.tags)

        # Anonymous/basic users only see public pages.
        if is_public:
            filtered_pages.append(page)
            continue
            
        # Blog readers can also see non-public blog posts.
        if can_read_blog and is_blog:
            filtered_pages.append(page)
            
    return filtered_pages


# --- Router Definition ---

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

@router.get("/stats", response_model=schemas.DashboardStats)
def read_dashboard_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    user_service: UserService = Depends(get_user_service),
    user: schemas.CurrentUser = Depends(get_current_user)
):
    """
    Retrieve aggregated statistics for the admin dashboard.

    The returned data is filtered based on the authenticated user's permissions.
    For example, users without 'form:read' will see 0 for form-related counts.
    """
    # 1. Get the full, unfiltered stats from the service layer.
    stats = dashboard_service.get_dashboard_stats()

    # 2. Get the user's permissions to perform checks.
    permissions = set(user_service.get_user_permissions(user.username))
    is_admin = "*" in permissions

    # 3. Apply RBAC filtering to the stats dictionary before returning it.
    
    # --- Filter Core Counts ---
    if not (is_admin or "page:read" in permissions):
        stats["core_counts"]["pages"] = 0
        stats["core_counts"]["tags"] = 0 # Tags are tied to content
    if not (is_admin or "form:read" in permissions):
        stats["core_counts"]["forms"] = 0
    if not (is_admin or "submission:read" in permissions):
        stats["core_counts"]["submissions"] = 0
    if not is_admin: # Only admins can see total user count
        stats["core_counts"]["users"] = 0

    # --- Filter Page Stats ---
    # Public count is always visible to everyone.
    if not (is_admin or "blog:read" in permissions):
        stats["page_stats"]["blog_posts_count"] = 0
        
    # --- Filter Activity Metrics ---
    # To see top forms, user needs to see both forms and their submissions.
    if not (is_admin or ("form:read" in permissions and "submission:read" in permissions)):
        stats["activity"]["top_forms_by_submission"] = []
    if not (is_admin or "page:read" in permissions):
        stats["activity"]["top_tags_on_pages"] = []
        
    # --- Filter Recent Items (Lists) ---
    if not (is_admin or "submission:read" in permissions):
        stats["recent_items"]["latest_submissions"] = []

    # For pages, we need to filter the lists themselves.
    stats["recent_items"]["newest_pages"] = _filter_page_list_for_user(
        stats["recent_items"]["newest_pages"], permissions
    )
    stats["recent_items"]["latest_updates"] = _filter_page_list_for_user(
        stats["recent_items"]["latest_updates"], permissions
    )
    
    # 4. Return the modified, permission-aware stats object.
    return stats

@router.get("/me", response_model=schemas.User)
def get_user(
    user_service: UserService = Depends(get_user_service),
    user: schemas.CurrentUser = Depends(get_current_user),
):
    """Returns Yourself"""
    return user_service.get_user_by_username(user.username)

@router.put("/me", response_model=schemas.User)
def update_yourself(
    update_data: schemas.UserUpdate,
    user_service: UserService = Depends(get_user_service),
    user: schemas.CurrentUser = Depends(get_current_user),
):
    """
    Update a user's details (role, display name, etc.).
    Note: This endpoint does NOT handle password changes.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Thou Art Not Logged In")
    
    return user_service.update_user(username=user.username, user_update=update_data)