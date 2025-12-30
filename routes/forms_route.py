from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data.database import get_db
from data import schemas 
from services.forms import FormService
from services.users import UserService
from src.dependencies import get_current_user, optional_user
from data.schemas import AlpineData, CurrentUser, SubmissionBase

# --- Dependency Setup ---
def get_form_service(db: Session = Depends(get_db)) -> FormService:
    return FormService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

router = APIRouter(prefix="/forms", tags=["Form"])

# ----------------------------------------------------
# 🧱 MODELS
# ----------------------------------------------------


# ----------------------------------------------------
# 🧩 FORMS CRUD
# ----------------------------------------------------

@router.post("/", response_model=schemas.Form, status_code=status.HTTP_201_CREATED)
def create_form(
    form_in: schemas.FormCreate,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(get_current_user),
):
    """Create a new custom form."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_create_form = "*" in user_permissions or "form:create" in user_permissions
    if can_create_form:
        form_in.author = user.username
        return form_service.create_new_form(form_data=form_in)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a form."
        )

@router.get("/list", response_model=List[schemas.Form])
def list_forms(
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(get_current_user),
):
    """List all available forms, optionally filtered by tag."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_read_form = "*" in user_permissions or "form:read" in user_permissions
    if not can_read_form:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to read a form."
        )
    
    all_forms = form_service.get_all_forms(skip=skip, limit=limit)
    
    if tag:
        # FIX: Iterate over f.tags (objects) and check if the tag string matches .name
        return [
            f for f in all_forms 
            if f.tags and any(t.name == tag for t in f.tags)
        ]
    
    return all_forms

@router.get("/{slug}", response_model=schemas.Form)
def get_form(
    slug: str,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(get_current_user),
):
    """Get a single form by its slug."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_read_form = "*" in user_permissions or "form:read" in user_permissions
    if not can_read_form:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to read a form."
        )
    return form_service.get_form_by_slug(slug)

@router.put("/{slug}", response_model=schemas.Form)
def update_form(
    slug: str,
    form_update: schemas.FormUpdate,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(get_current_user),
):
    """Update an existing form definition."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_update_form = "*" in user_permissions or "form:update" in user_permissions
    if not can_update_form:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update a form."
        )
    return form_service.update_existing_form(slug=slug, form_update_data=form_update)

@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form(
    slug: str,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(get_current_user),
):
    """Delete a form and all its submissions by its slug."""
    user_permissions = user_service.get_user_permissions(user.username)
    can_delete_form = "*" in user_permissions or "form:delete" in user_permissions
    if not can_delete_form:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete a form."
        )
    form_service.delete_form_by_slug(slug)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ----------------------------------------------------
# 🏷️ TAG UTILITIES
# ----------------------------------------------------

@router.get("/tags/all", response_model=List[str])
def get_all_tags(
    form_service: FormService = Depends(get_form_service),
    user: CurrentUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),  
):
    """Get a list of all unique tags across all forms."""
    user_permissions = user_service.get_user_permissions(user.username)
    permission = "*" in user_permissions or "form:read" in user_permissions
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this route."
        )
    forms = form_service.get_all_forms(skip=0, limit=1000)
    
    tags = set()
    for form in forms:
        if form.tags:
            # FIX: Extract .name from the objects
            tags.update(tag.name for tag in form.tags) 
    return sorted(list(tags))

# ----------------------------------------------------
# 📨 FORM SUBMISSIONS
# ----------------------------------------------------

@router.post("/{slug}/submit", response_model=schemas.Submission, status_code=status.HTTP_201_CREATED)
def submit_form(
    slug: str,
    submission_body: SubmissionBase,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(optional_user),
):
    """Submit a response to a form."""
    form = form_service.get_form_by_slug(slug)
    
    # FIX: Convert list of objects to set of strings
    form_tag_names = {tag.name for tag in (form.tags or [])}

    user_permissions = []
    user_role = "anon" 

    if user:
        user_permissions = user_service.get_user_permissions(user.username)
        user_role = user.role

    override_submission = "*" in user_permissions or "submission:create" in user_permissions
    # FIX: Check against the string set
    form_is_open = "any:create" in form_tag_names
    
    role_is_allowed = f"{user_role}:create" in form_tag_names

    if override_submission:
        pass
    elif role_is_allowed:
        pass
    elif form_is_open:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add submission in this form."
        )
    
    author_username = user.username if user else "Anon"
    
    submission_data = schemas.SubmissionCreate(
        form_slug=slug,
        data=submission_body.data,
        custom=submission_body.custom,
        author=author_username
    )
    
    return form_service.create_new_submission(submission_data=submission_data)

@router.get("/{slug}/submissions", response_model=List[schemas.Submission])
def list_submissions(
    slug: str,
    skip: int = 0,
    limit: int = 100,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),  
    user: CurrentUser = Depends(get_current_user),
):
    """List all submissions for a form."""
    form = form_service.get_form_by_slug(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # FIX: Extract tag names
    form_tag_names = {tag.name for tag in (form.tags or [])}

    user_permissions = user_service.get_user_permissions(user.username)
    override_submission = "*" in user_permissions or "submission:read" in user_permissions
    
    # FIX: Check against string set
    form_is_open = "any:read" in form_tag_names
    role_is_allowed = f"{user.role}:read" in form_tag_names
    
    if not override_submission and not form_is_open and not role_is_allowed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        
    return form_service.get_submissions_for_form(form_slug=slug, skip=skip, limit=limit)

@router.get("/{slug}/submissions/{submission_id}", response_model=schemas.Submission)
def get_submission(
    slug: str,
    submission_id: int,
    form_service: FormService = Depends(get_form_service),
    user_service: UserService = Depends(get_user_service),
    user: CurrentUser = Depends(get_current_user),
):
    form = form_service.get_form_by_slug(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    submission = form_service.get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # FIX: Extract tag names
    form_tag_names = {tag.name for tag in (form.tags or [])}

    user_permissions = user_service.get_user_permissions(user.username)

    override_submission = ("*" in user_permissions or "submission:read" in user_permissions)
    
    # FIX: Check against string set
    form_is_open = "any:read" in form_tag_names
    role_is_allowed = f"{user.role}:read" in form_tag_names
    user_owns_it = submission.author == user.username

    authorized = (
        override_submission or
        form_is_open or
        role_is_allowed or
        user_owns_it
    )

    if not authorized:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission.form_slug != slug:
        raise HTTPException(status_code=404, detail="Submission not found for this form.")

    return submission


@router.put("/{slug}/submissions/{submission_id}", response_model=schemas.Submission)
def update_submission(
    slug: str,
    submission_id: int,
    submission_update: schemas.SubmissionUpdate,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
    user_service: UserService = Depends(get_user_service),
):
    form = form_service.get_form_by_slug(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    # FIX: Extract tag names once
    form_tag_names = {tag.name for tag in (form.tags or [])}

    if user is None:
        # FIX: Check against string set
        if "any:update" not in form_tag_names:
            raise HTTPException(status_code=404, detail="Submission not found")

    submission = form_service.get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # FIX: Handle permissions safely for optional user
    user_permissions = []
    user_role = "anon"
    if user:
        user_permissions = user_service.get_user_permissions(user.username)
        user_role = user.role

    override_update = ("*" in user_permissions or "submission:update" in user_permissions)

    # FIX: Check against string set using safe variables
    form_is_open_for_update = "any:update" in form_tag_names
    role_is_allowed = f"{user_role}:update" in form_tag_names
    user_owns_it = user and submission.author == user.username

    authorized = (
        override_update or
        form_is_open_for_update or
        role_is_allowed or
        user_owns_it
    )

    if not authorized:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.form_slug != slug:
        raise HTTPException(status_code=404, detail="Submission not found for this form.")

    return form_service.update_submission(submission_id=submission_id, submission_data=submission_update)


@router.delete("/{slug}/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(
    slug: str,
    submission_id: int,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
    user_service: UserService = Depends(get_user_service),
):
    form = form_service.get_form_by_slug(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Submission not found")

    # FIX: Extract tag names once
    form_tag_names = {tag.name for tag in (form.tags or [])}

    if user is None:
        # FIX: Check against string set
        if "any:delete" not in form_tag_names:
            raise HTTPException(status_code=404, detail="Submission not found")

    submission = form_service.get_submission_by_id(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # FIX: Handle permissions safely for optional user
    user_permissions = []
    user_role = "anon"
    if user:
        user_permissions = user_service.get_user_permissions(user.username)
        user_role = user.role

    override_delete = ("*" in user_permissions or "submission:delete" in user_permissions)

    # FIX: Check against string set using safe variables
    form_is_open_for_delete = "any:delete" in form_tag_names
    role_is_allowed = f"{user_role}:delete" in form_tag_names
    user_owns_it = user and submission.author == user.username

    authorized = (
        override_delete or
        form_is_open_for_delete or
        role_is_allowed or
        user_owns_it
    )

    if not authorized:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.form_slug != slug:
        raise HTTPException(status_code=404, detail="Submission not found")

    form_service.delete_submission_by_id(submission_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

