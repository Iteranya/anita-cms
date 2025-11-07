from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any, Dict, List, Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.config import load_or_create_config, save_config, load_or_create_mail_config, save_mail_config
from data import db, forms_db  # Import the db module with standalone functions
from data.models import Page as PageData
from src.auth import get_current_user, optional_auth
from datetime import datetime

router = APIRouter(prefix="/forms", tags=["Form"])

class FormModel(BaseModel):
    """Represents a custom form definition."""
    slug: str
    title: str
    schema: Dict[str, Any]  # e.g. {"fields": [{"name": "email", "type": "text"}]}
    description: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}

class FormSubmissionModel(BaseModel):
    """Represents a single submission to a form."""
    id: Optional[int] = None
    form_slug: str
    data: Dict[str, Any]  # user responses
    created: Optional[str] = None
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}

# ----------------------------------------------------
# 🧱 FORMS CRUD
# ----------------------------------------------------

@router.post("/", response_model=FormModel)
def create_form(form: FormModel, user=Depends(get_current_user)):
    """Create a new custom form."""
    existing = forms_db.get_form(form.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Form slug already exists.")
    now = datetime.now().isoformat()
    form.created = now
    form.updated = now
    form.author = user.username if user else None
    forms_db.add_form(form.slug, form.title, form.schema)
    return form


@router.get("/", response_model=List[FormModel])
def list_forms(user=Depends(optional_auth)):
    """List all available forms."""
    return forms_db.list_forms()


@router.get("/{slug}", response_model=FormModel)
def get_form(slug: str, user=Depends(optional_auth)):
    """Get a single form by its slug."""
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    return form


@router.put("/{slug}", response_model=FormModel)
def update_form(slug: str, form: FormModel, user=Depends(get_current_user)):
    """Update an existing form definition."""
    existing = forms_db.get_form(slug)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found.")
    form.updated = datetime.now().isoformat()
    forms_db.update_form(form)  # We'll add this in forms_db
    return form


@router.delete("/{slug}")
def delete_form(slug: str, user=Depends(get_current_user)):
    """Delete a form by its slug."""
    existing = forms_db.get_form(slug)
    if not existing:
        raise HTTPException(status_code=404, detail="Form not found.")
    forms_db.delete_form(slug)
    return {"detail": f"Form '{slug}' deleted successfully."}


# ----------------------------------------------------
# 📨 FORM SUBMISSIONS
# ----------------------------------------------------

@router.post("/{slug}/submit", response_model=FormSubmissionModel)
def submit_form(slug: str, submission: FormSubmissionModel, user=Depends(optional_auth)):
    """Submit a response to a form."""
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    submission.form_slug = slug
    submission.created = datetime.now().isoformat()
    submission.author = getattr(user, "username", None) if user else None
    forms_db.add_submission(slug, submission.data)
    return submission


@router.get("/{slug}/submissions", response_model=List[FormSubmissionModel])
def list_submissions(slug: str, user=Depends(get_current_user)):
    """List all submissions for a form."""
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    submissions = forms_db.list_submissions(slug)
    return submissions

@router.put("/{slug}/submissions/{submission_id}", response_model=FormSubmissionModel)
def update_submission(
    slug: str,
    submission_id: int,
    updated_submission: FormSubmissionModel,
    user=Depends(get_current_user)
):
    """Update a specific submission for a form."""
    # Make sure the form exists
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    # Check if submission exists
    existing = forms_db.get_submission(submission_id)
    if not existing or existing["form_slug"] != slug:
        raise HTTPException(status_code=404, detail="Submission not found.")

    # Update metadata
    updated_submission.id = submission_id
    updated_submission.form_slug = slug
    updated_submission.updated = datetime.now().isoformat()
    updated_submission.author = getattr(user, "username", None)

    forms_db.update_submission(updated_submission)
    return updated_submission

@router.delete("/{slug}/submissions/{submission_id}")
def delete_submission(slug: str, submission_id: int, user=Depends(get_current_user)):
    """Delete a specific submission from a form."""
    # Verify the form exists
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    # Verify the submission exists
    submission = forms_db.get_submission(submission_id)
    if not submission or submission["form_slug"] != slug:
        raise HTTPException(status_code=404, detail="Submission not found.")

    forms_db.delete_submission(submission_id)
    return {"detail": f"Submission {submission_id} deleted successfully."}
