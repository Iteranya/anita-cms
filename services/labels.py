from sqlalchemy.orm import Session
from typing import List

from data import crud

class LabelService:
    def __init__(self, db: Session):
        self.db = db
    def get_main_label(self) -> List[str]:
        """
        Retrieves all existing page groups
        """
        return crud.get_main_labels(db=self.db)