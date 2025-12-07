from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Any, Dict, List, Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# --- New Imports for Service-Oriented Architecture ---
from data.database import get_db
from data import schemas  # Import Pydantic schemas from your data layer
from services.forms import FormService
from src.dependencies import get_current_user, optional_user
from data.schemas import User as CurrentUser

# --- Dependency Setup ---
# This function allows FastAPI to inject the FormService into our routes.
def get_form_service(db: Session = Depends(get_db)) -> FormService:
    return FormService(db)

router = APIRouter(prefix="/forms", tags=["Form"])

# ----------------------------------------------------
# 🧱 MODELS (for request bodies not covered by schemas)
# ----------------------------------------------------

class SubmissionBody(BaseModel):
    """
    Represents the expected JSON body for a new submission.
    It intentionally omits fields that are derived from the context,
    like form_slug (from URL), id, author, and timestamps (from server).
    """
    data: Dict[str, Any]
    custom: Optional[Dict[str, Any]] = {}

# ----------------------------------------------------
# 🖼️ FORM HTML VIEW
# ----------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request, user: Optional[CurrentUser] = Depends(optional_user)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # This logic remains the same as it's for serving a UI template.
    template_path = "static/form/index.html"
    slug = request.query_params.get("slug", "")
    with open(template_path, "r") as f:
        html = f.read()
    html = html.replace(
        '<div id="slug-container" style="display: none;" data-slug=""></div>',
        f'<div id="slug-container" style="display: none;" data-slug="{slug}">{slug}</div>'
    )
    return html

# ----------------------------------------------------
# 🧩 FORMS CRUD
# ----------------------------------------------------

@router.post("/", response_model=schemas.Form, status_code=status.HTTP_201_CREATED)
def create_form(
    form_in: schemas.FormCreate,
    form_service: FormService = Depends(get_form_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Create a new custom form."""
    form_in.author = user.username
    # The service now handles checking for existing slugs and other business logic.
    return form_service.create_new_form(form_data=form_in)

@router.get("/list", response_model=List[schemas.Form])
def list_forms(
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user), # Kept for potential future use
):
    """List all available forms, optionally filtered by tag."""
    all_forms = form_service.get_all_forms(skip=skip, limit=limit)
    
    # Filtering by tag is done here as it's a presentation-layer concern.
    # For performance on large datasets, this filter should be moved to the service/CRUD layer.
    if tag:
        return [f for f in all_forms if f.tags and tag in f.tags]
    
    return all_forms

@router.get("/{slug}", response_model=schemas.Form)
def get_form(
    slug: str,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
):
    """Get a single form by its slug."""
    form = form_service.get_form_by_slug(slug)
    
    # Authorization logic remains in the route layer.
    if form.tags and "read" not in form.tags and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    return form

@router.put("/{slug}", response_model=schemas.Form)
def update_form(
    slug: str,
    form_update: schemas.FormUpdate,
    form_service: FormService = Depends(get_form_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Update an existing form definition."""
    # The service handles checking for existence and performing the update.
    return form_service.update_existing_form(slug=slug, form_update_data=form_update)

@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form(
    slug: str,
    form_service: FormService = Depends(get_form_service),
    user: CurrentUser = Depends(get_current_user),
):
    """Delete a form and all its submissions by its slug."""
    form_service.delete_form_by_slug(slug)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ----------------------------------------------------
# 🏷️ TAG UTILITIES
# ----------------------------------------------------

@router.get("/tags/all", response_model=List[str])
def get_all_tags(
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
):
    """Get a list of all unique tags across all forms."""
    forms = form_service.get_all_forms(skip=0, limit=1000) # Adjust limit as needed
    tags = set()
    for form in forms:
        if form.tags:
            tags.update(form.tags)
    return sorted(list(tags))

# ----------------------------------------------------
# 📨 FORM SUBMISSIONS
# ----------------------------------------------------

@router.post("/{slug}/submit", response_model=schemas.Submission, status_code=status.HTTP_201_CREATED)
def submit_form(
    slug: str,
    submission_body: SubmissionBody,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
):
    """Submit a response to a form."""
    form = form_service.get_form_by_slug(slug)
    
    # Authorization check
    if form.tags and "create" not in form.tags and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    author_username = user.username if user else None
    
    # Construct the full submission data object for the service layer.
    submission_data = schemas.SubmissionCreate(
        form_slug=slug,
        data=submission_body.data,
        custom=submission_body.custom,
        author=author_username
    )
    
    # The service validates the data against the form's schema before saving.
    return form_service.create_new_submission(submission_data=submission_data)

@router.get("/{slug}/submissions", response_model=List[schemas.Submission])
def list_submissions(
    slug: str,
    skip: int = 0,
    limit: int = 100,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
):
    """List all submissions for a form."""
    form = form_service.get_form_by_slug(slug)
    
    # Authorization check
    if form.tags and "read" not in form.tags and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        
    return form_service.get_submissions_for_form(form_slug=slug, skip=skip, limit=limit)

@router.get("/{slug}/submissions/{submission_id}", response_model=schemas.Submission)
def get_submission(
    slug: str,
    submission_id: int,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
):
    """Get a specific submission from a form."""
    form = form_service.get_form_by_slug(slug)
    
    # Authorization check
    if form.tags and "read" not in form.tags and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    submission = form_service.get_submission_by_id(submission_id)
    if submission.form_slug != slug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found for this form.")
    
    return submission

@router.put("/{slug}/submissions/{submission_id}", response_model=schemas.Submission)
def update_submission(
    slug: str,
    submission_id: int,
    submission_update: schemas.SubmissionUpdate, # Assumes a SubmissionUpdate schema exists
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
):
    """
    Update a specific submission. 
    NOTE: This requires `update_submission` to be implemented in FormService and CRUD layer.
    """
    form = form_service.get_form_by_slug(slug)

    # Authorization check
    if form.tags and "update" not in form.tags and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Verify submission exists and belongs to the correct form before updating
    submission = form_service.get_submission_by_id(submission_id)
    if submission.form_slug != slug:
        raise HTTPException(status_code=404, detail="Submission not found for this form.")
    
    # Placeholder for the actual service call
    # return form_service.update_submission(submission_id, submission_update)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Update submission functionality not implemented in the service layer.")


@router.delete("/{slug}/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(
    slug: str,
    submission_id: int,
    form_service: FormService = Depends(get_form_service),
    user: Optional[CurrentUser] = Depends(optional_user),
):
    """Delete a specific submission."""
    form = form_service.get_form_by_slug(slug)
    
    # Authorization check
    if form.tags and "delete" not in form.tags and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    # Verify submission exists and belongs to the correct form before deleting
    submission = form_service.get_submission_by_id(submission_id)
    if submission.form_slug != slug:
        raise HTTPException(status_code=404, detail="Submission not found for this form.")
        
    form_service.delete_submission_by_id(submission_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)