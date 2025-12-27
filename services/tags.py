from sqlalchemy.orm import Session
from typing import List

from data import crud

class TagService:
    def __init__(self, db: Session):
        self.db = db
    def get_main_tag(self) -> List[str]:
        """
        Retrieves all existing page groups
        """
        return crud.get_main_tags(db=self.db)