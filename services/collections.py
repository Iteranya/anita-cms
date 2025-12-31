# file: services/collections.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from data import crud, schemas, models
from typing import List, Dict, Any, Set

class CollectionService:
    def __init__(self, db: Session):
        self.db = db

    # --- Collection Methods ---

    def get_collection_by_slug(self, slug: str) -> models.Collection:
        """
        Gets a collection by slug, raising a standard 404 exception if not found.
        This is a common utility function used by other methods in this service.
        """
        collection = crud.get_collection(self.db, slug=slug)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection with slug '{slug}' not found."
            )
        return collection

    def get_all_collections(self, skip: int, limit: int) -> List[models.Collection]:
        """Gets a list of all available collections."""
        return crud.list_collections(self.db, skip=skip, limit=limit)

    def create_new_collection(self, collection_data: schemas.CollectionCreate) -> models.Collection:
        """
        Creates a new collection after performing business logic checks.
        """
        # Business Logic 1: Check for slug uniqueness.
        existing_collection = crud.get_collection(self.db, slug=collection_data.slug)
        if existing_collection:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Collection with slug '{collection_data.slug}' already exists."
            )

        # Business Logic 2 (Example): Ensure the schema is not empty.
        if not collection_data.schema:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Collection schema cannot be empty."
            )
        
        # If all checks pass, proceed to create the collection in the database.
        return crud.create_collection(self.db, collection=collection_data)

    def update_existing_collection(self, slug: str, collection_update_data: schemas.CollectionUpdate) -> models.Collection:
        """
        Updates an existing collection.
        """
        # First, ensure the collection we're trying to update actually exists.
        self.get_collection_by_slug(slug)
        
        # Then, call the CRUD function to perform the update.
        updated_collection = crud.update_collection(self.db, slug=slug, collection_update=collection_update_data)
        if not updated_collection:
             # This case is unlikely if get_collection_by_slug passed, but good for safety
            raise HTTPException(status_code=500, detail="Could not update collection.")

        return updated_collection

    def delete_collection_by_slug(self, slug: str):
        """
        Deletes a collection and all its associated submissions (due to DB cascade).
        """
        # Ensure the collection exists before attempting deletion.
        self.get_collection_by_slug(slug)
        
        success = crud.delete_collection(self.db, slug=slug)
        if not success:
            # This case is unlikely if get_collection_by_slug passed, but good for safety
            raise HTTPException(status_code=500, detail="Could not delete collection.")

    # --- Submission Methods ---

    def _validate_submission_data(self, schema: Dict[str, Any], data: Dict[str, Any]):
        """
        A simple validator to check if submission data concollections to the collection's schema.
        """
        
        # 1. Extract the names of all valid fields from the schema's 'fields' list.
        #    Using a set is more efficient for membership checking ('in').
        try:
            valid_field_names: Set[str] = {field['name'] for field in schema['fields']}
        except (KeyError, TypeError):
            # Handle cases where the schema format is not what we expect
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server has a misconfigured collection schema."
            )

        # 2. Check for extra fields not defined in the schema
        for field_name in data:
            # 3. Now, check if the field_name is in our set of valid names
            if field_name not in valid_field_names:
                print(f"Schema's valid fields: {valid_field_names}")
                print(f"Unexpected field in submission: '{field_name}'")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Unexpected field in submission: '{field_name}'"
                )

    def create_new_submission(self, submission_data: schemas.SubmissionCreate) -> models.Submission:
        """
        Creates a new submission for a collection after validation.
        """
        # Business Logic 1: The collection must exist to accept a submission.
        collection = self.get_collection_by_slug(submission_data.collection_slug)
        
        # Business Logic 2: Validate the incoming data against the collection's schema.
        self._validate_submission_data(schema=collection.schema, data=submission_data.data)

        # If validation passes, create the submission.
        return crud.create_submission(self.db, submission=submission_data)

    def get_submissions_for_collection(self, collection_slug: str, skip: int = 0, limit: int = 100) -> List[models.Submission]:
        """
        Retrieves all submissions for a specific collection.
        """
        # Ensure the parent collection exists.
        self.get_collection_by_slug(collection_slug)
        
        return crud.list_submissions(self.db, collection_slug=collection_slug, skip=skip, limit=limit)

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
    
    def update_submission(self, submission_id: int, submission_data: schemas.SubmissionUpdate) -> models.Submission:
        """
        Updates an existing submission after validating the new data against the collection schema.
        """
        # 1. Get the current submission to ensure it exists and to find its parent collection.
        #    (Even though the route checks this, the service should be self-contained).
        current_submission = self.get_submission_by_id(submission_id)

        # 2. If the update includes new collection 'data', we must validate it against the schema.
        if submission_data.data is not None:
            # Fetch the parent collection to access the validation schema
            collection = self.get_collection_by_slug(current_submission.collection_slug)
            
            # Validate the new data
            self._validate_submission_data(schema=collection.schema, data=submission_data.data)

        # 3. Call the CRUD operation
        updated_submission = crud.update_submission(
            self.db, 
            submission_id=submission_id, 
            submission_update=submission_data
        )

        if not updated_submission:
            raise HTTPException(status_code=500, detail="Could not update submission.")

        return updated_submission
    

    def delete_submission_by_id(self, submission_id: int):
        """
        Deletes a single submission by its ID.
        """
        # Ensure the submission exists before attempting to delete it.
        self.get_submission_by_id(submission_id)
        
        success = crud.delete_submission(self.db, submission_id=submission_id)
        if not success:
            raise HTTPException(status_code=500, detail="Could not delete submission.")