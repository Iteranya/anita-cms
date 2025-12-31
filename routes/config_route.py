# file: api/admin.py

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Local imports
from data.database import get_db
# Assuming the ConfigService you provided is saved in services/config.py
from services.config import ConfigService 
from src.dependencies import require_admin

router = APIRouter(prefix="/config", tags=["Config"])

# --- Local Schema for Config ---
# We define this here (or in schemas.py) to validate the specific 
# shape of the monolithic configuration object used by the Admin UI.
class SystemConfiguration(BaseModel):
    system_note: str = "You are a friendly AI Assistant."
    ai_endpoint: str
    base_llm: str
    temperature: float
    ai_key: Optional[str] = ""
    theme: Optional[str] = "default"
    # Routes is a complex list of dicts, we keep it flexible
    routes: Optional[List[Dict[str, Any]]] = []

    class Config:
        from_attributes = True

@router.get("/", response_model=SystemConfiguration)
def get_config(
    user: dict = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """
    Load all system settings from the database. 
    If they don't exist, ConfigService will return defaults.
    """
    service = ConfigService(db)
    
    # Ensure defaults exist if DB is empty
    service.seed_initial_settings()
    
    settings = service.get_all_settings()
    return settings

@router.post("/", response_model=SystemConfiguration)
def update_config(
    updated: SystemConfiguration, 
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update system configuration. 
    Accepts the full config object, validates it via ConfigService, 
    and saves changes to the database.
    """
    service = ConfigService(db)
    
    # Convert Pydantic model to a standard dictionary
    settings_data = updated.model_dump()

    # If ai_key is empty string or None, we might want to handle it carefully.
    # Currently, this overwrites values with whatever is sent.
    
    saved_settings = service.save_settings(settings_data)
    return saved_settings