# file: services/forms.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from data import crud, schemas, models
from typing import List, Dict, Any

class FormService:
    def __init__(self, db: Session):
        self.db = db

    # --- Form Methods ---

    def get_form_by_slug(self, slug: str) -> models.Form:
        """
        Gets a form by slug, raising a standard 404 exception if not found.
        This is a common utility function used by other methods in this service.
        """
        form = crud.get_form(self.db, slug=slug)
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Form with slug '{slug}' not found."
            )
        return form

    def get_all_forms(self, skip: int, limit: int) -> List[models.Form]:
        """Gets a list of all available forms."""
        return crud.list_forms(self.db, skip=skip, limit=limit)

    def create_new_form(self, form_data: schemas.FormCreate) -> models.Form:
        """
        Creates a new form after performing business logic checks.
        """
        # Business Logic 1: Check for slug uniqueness.
        existing_form = crud.get_form(self.db, slug=form_data.slug)
        if existing_form:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Form with slug '{form_data.slug}' already exists."
            )

        # Business Logic 2 (Example): Ensure the schema is not empty.
        if not form_data.schema_:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form schema cannot be empty."
            )
        
        # If all checks pass, proceed to create the form in the database.
        return crud.create_form(self.db, form=form_data)

    def update_existing_form(self, slug: str, form_update_data: schemas.FormUpdate) -> models.Form:
        """
        Updates an existing form.
        """
        # First, ensure the form we're trying to update actually exists.
        self.get_form_by_slug(slug)
        
        # Then, call the CRUD function to perform the update.
        updated_form = crud.update_form(self.db, slug=slug, form_update=form_update_data)
        if not updated_form:
             # This case is unlikely if get_form_by_slug passed, but good for safety
            raise HTTPException(status_code=500, detail="Could not update form.")

        return updated_form

    def delete_form_by_slug(self, slug: str):
        """
        Deletes a form and all its associated submissions (due to DB cascade).
        """
        # Ensure the form exists before attempting deletion.
        self.get_form_by_slug(slug)
        
        success = crud.delete_form(self.db, slug=slug)
        if not success:
            # This case is unlikely if get_form_by_slug passed, but good for safety
            raise HTTPException(status_code=500, detail="Could not delete form.")

    # --- Submission Methods ---

    def _validate_submission_data(self, schema: Dict[str, Any], data: Dict[str, Any]):
        """
        A simple validator to check if submission data conforms to the form's schema.
        NOTE: For production, a more robust library like `jsonschema` would be better.
        """
        # Check for required fields
        for field_name, field_props in schema.items():
            if field_props.get("required", False) and field_name not in data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required field: '{field_name}'"
                )
        
        # Check for extra fields not in the schema
        for field_name in data:
            if field_name not in schema:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Unexpected field in submission: '{field_name}'"
                )

    def create_new_submission(self, submission_data: schemas.SubmissionCreate) -> models.Submission:
        """
        Creates a new submission for a form after validation.
        """
        # Business Logic 1: The form must exist to accept a submission.
        form = self.get_form_by_slug(submission_data.form_slug)
        
        # Business Logic 2: Validate the incoming data against the form's schema.
        self._validate_submission_data(schema=form.schema_, data=submission_data.data)

        # If validation passes, create the submission.
        return crud.create_submission(self.db, submission=submission_data)

    def get_submissions_for_form(self, form_slug: str, skip: int, limit: int) -> List[models.Submission]:
        """
        Retrieves all submissions for a specific form.
        """
        # Ensure the parent form exists.
        self.get_form_by_slug(form_slug)
        
        return crud.list_submissions(self.db, form_slug=form_slug, skip=skip, limit=limit)

    def get_submission_by_id(self, submission_id: int) -> models.Submission:
        """
        Gets a single submission by its ID, raising 404 if not found.
        """
        submission = crud.get_submission(self.db, submission_id=submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Submission with ID {submission_id} not found."
            )
        return submission

    def delete_submission_by_id(self, submission_id: int):
        """
        Deletes a single submission by its ID.
        """
        # Ensure the submission exists before attempting to delete it.
        self.get_submission_by_id(submission_id)
        
        success = crud.delete_submission(self.db, submission_id=submission_id)
        if not success:
            raise HTTPException(status_code=500, detail="Could not delete submission.")