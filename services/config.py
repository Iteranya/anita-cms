# services/config_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any, Optional
import json

from data import crud

# Helper to load defaults from the canonical JSON file
def _get_default_config() -> Dict[str, Any]:
    try:
        with open("default_settings.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to a minimal config if file is missing/corrupt
        return {"system_note": "Default note: config file missing."}

class ConfigService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Retrieves all settings from the database and merges them with the
        hardcoded defaults from the JSON file for a complete view.
        """
        defaults = _get_default_config()
        db_settings = crud.get_all_settings(self.db)
        
        # Start with defaults, then override with any values from the database
        defaults.update(db_settings)
        return defaults

    def get_setting_value(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Retrieves the value for a single setting by its key.
        Checks DB first, then falls back to the default JSON config.
        """
        value = crud.get_setting(self.db, key=key)
        
        if value is not None:
            return value

        # If not in DB, fall back to the value from the default JSON file
        return _get_default_config().get(key, default)


    def _validate_setting(self, key: str, value: Any):
        """
        A private method for running business logic validation on specific settings.
        This ensures data integrity before saving to the database.
        """
        if key == "temperature":
            if not isinstance(value, (int, float)) or not (0.0 <= value <= 2.0):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Setting 'temperature' must be a number between 0.0 and 2.0."
                )
        
        if key == "routes":
            if not isinstance(value, list):
                 raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Setting 'routes' must be a valid JSON array."
                )
            for i, route in enumerate(value):
                if not isinstance(route, dict) or "name" not in route or "schema" not in route:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Route at index {i} is invalid. It must be an object with 'name' and 'schema' keys."
                    )
        
        if key in ["ai_key", "theme", "system_note", "ai_endpoint", "base_llm"]:
            if not isinstance(value, str):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Setting '{key}' must be a string."
                )

    def save_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves a dictionary of settings to the database.
        Each key-value pair in the dictionary will be validated and saved as a
        separate setting row.
        """
        for key, value in settings_data.items():
            self._validate_setting(key, value)
            crud.save_setting(self.db, key=key, value=value)
        
        return self.get_all_settings()

    def seed_initial_settings(self):
        """
        Calls the data layer to seed the database from default_settings.json
        if no settings currently exist.
        """
        # The logic now correctly resides in the crud layer.
        crud.seed_initial_settings(self.db)