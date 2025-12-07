# file: services/pages.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from data import crud, schemas, models

class PageService:
    def __init__(self, db: Session):
        self.db = db

    def get_page_by_slug(self, slug: str) -> models.Page:
        """
        Gets a page by slug, raising a standard 404 exception if not found.
        """
        page = crud.get_page(self.db, slug=slug)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page with slug '{slug}' not found."
            )
        return page

    def get_all_pages(self, skip: int, limit: int) -> list[models.Page]:
        """Gets a list of all pages."""
        return crud.list_pages(self.db, skip=skip, limit=limit)

    def create_new_page(self, page_data: schemas.PageCreate) -> models.Page:
        """
        Creates a new page after performing business logic checks.
        """
        # --- EXAMPLE BUSINESS LOGIC ---
        # 1. Check for forbidden slugs.
        forbidden_slugs = {"admin", "api", "login", "static"}
        if page_data.slug in forbidden_slugs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The slug '{page_data.slug}' is a reserved keyword."
            )

        # 2. Check for slug uniqueness.
        existing_page = crud.get_page(self.db, slug=page_data.slug)
        if existing_page:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Page with slug '{page_data.slug}' already exists."
            )

        # 3. If all checks pass, call the CRUD function to create the page.
        new_page = crud.create_page(self.db, page=page_data)
        
        # --- MORE EXAMPLE BUSINESS LOGIC ---
        # 4. You could send an email notification here.
        #    send_notification(f"New page created: {new_page.title}")
        # 5. You could log this action to an audit trail.
        #    log_audit(user="current_user", action=f"Created page {new_page.slug}")

        return new_page
        
    def update_existing_page(self, slug: str, page_update_data: schemas.PageUpdate) -> models.Page:
        """
        Updates an existing page.
        """
        # First, ensure the page exists.
        db_page = self.get_page_by_slug(slug)
        
        # Call the CRUD function to perform the update.
        updated_page = crud.update_page(self.db, slug=db_page.slug, page_update=page_update_data)
        
        return updated_page

    def delete_page_by_slug(self, slug: str):
        """
        Deletes a page.
        """
        # First, ensure the page exists.
        self.get_page_by_slug(slug)

        # Call the CRUD function.
        crud.delete_page(self.db, slug=slug)

        # Return nothing, as the router will handle the 204 response.