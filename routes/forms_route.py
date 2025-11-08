from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any, Dict, List, Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime

from src.config import load_or_create_config, save_config, load_or_create_mail_config, save_mail_config
from data import forms_db  # Your database helper module
from src.auth import get_current_user, optional_auth

router = APIRouter(prefix="/forms", tags=["Form"])

# ----------------------------------------------------
# 🧱 MODELS
# ----------------------------------------------------

class FormModel(BaseModel):
    """Represents a custom form definition."""
    slug: str
    title: str
    schema: Dict[str, Any]
    description: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}


class FormSubmissionModel(BaseModel):
    """Represents a single submission to a form."""
    id: Optional[int] = None
    form_slug: str
    data: Dict[str, Any]
    created: Optional[str] = None
    updated: Optional[str] = None
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}

# ----------------------------------------------------
# 🖼️ FORM HTML VIEW
# ----------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request, user: Optional[str] = Depends(optional_auth)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

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

@router.post("/", response_model=FormModel)
def create_form(form: FormModel, user=Depends(get_current_user)):
    """Create a new custom form."""
    existing = forms_db.get_form(form.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Form slug already exists.")

    now = datetime.now().isoformat()
    form.created = now
    form.updated = now
    form.author = getattr(user, "username", "Admin")

    forms_db.add_form(
        form.slug,
        form.title,
        form.schema,
        author=form.author,
        custom=form.custom
    )
    return form


@router.get("/list", response_model=List[FormModel])
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
    forms_db.update_form(form)
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
        print("Form Not Found")
        raise HTTPException(status_code=404, detail="Form not found.")
    print("NYOOOOOM~")
    now = datetime.now().isoformat()
    submission.form_slug = slug
    submission.created = now
    submission.updated = now
    submission.author = getattr(user, "username", None) if user else None

    forms_db.add_submission(
        form_slug=slug,
        data=submission.data,
        author=submission.author,
        custom=submission.custom
    )
    return submission


@router.get("/{slug}/submissions", response_model=List[FormSubmissionModel])
def list_submissions(slug: str, user=Depends(get_current_user)):
    """List all submissions for a form."""
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    return forms_db.list_submissions(slug)


@router.put("/{slug}/submissions/{submission_id}", response_model=FormSubmissionModel)
def update_submission(
    slug: str,
    submission_id: int,
    updated_submission: FormSubmissionModel,
    user=Depends(get_current_user)
):
    """Update a specific submission for a form."""
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    existing = forms_db.get_submission(submission_id)
    if not existing or existing["form_slug"] != slug:
        raise HTTPException(status_code=404, detail="Submission not found.")

    updated_submission.id = submission_id
    updated_submission.form_slug = slug
    updated_submission.updated = datetime.now().isoformat()
    updated_submission.author = getattr(user, "username", None)

    forms_db.update_submission(updated_submission)
    return updated_submission


@router.delete("/{slug}/submissions/{submission_id}")
def delete_submission(slug: str, submission_id: int, user=Depends(get_current_user)):
    """Delete a specific submission from a form."""
    form = forms_db.get_form(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    submission = forms_db.get_submission(submission_id)
    if not submission or submission["form_slug"] != slug:
        raise HTTPException(status_code=404, detail="Submission not found.")

    forms_db.delete_submission(submission_id)
    return {"detail": f"Submission {submission_id} deleted successfully."}
