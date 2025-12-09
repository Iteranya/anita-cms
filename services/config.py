from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any, Optional

from data import crud, schemas

DEFAULT_CONFIG = {
  "system_note": "You are a friendly AI Assistant, Do as you are instructed to.",
  "ai_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent",
  "base_llm": "gemini-1.5-pro-latest",
  "temperature": 0.5,
  "ai_key": "",
  "theme": "default",
  "routes": [
    {
      "name": "media_get_file",
      "schema": {
        "method": "GET",
        "path": "/media/{filename}",
        "params": { "filename": "string" },
        "returns": "Binary Image File (Blob)"
      },
      "type": "media",
      "description": "Retrieve an uploaded media file directly."
    },
    {
      "name": "media_upload",
      "schema": {
        "method": "POST",
        "path": "/media",
        "body": {
          "files": "List[UploadFile]"
        },
        "auth": True,
        "returns": {
          "status": "string",
          "total": "int",
          "files": "List[{ 'original': string, 'saved_as': string, 'url': string, 'size': int, 'format_chosen': string }]"
        }
      },
      "type": "media",
      "description": "Upload images. Returns a JSON list. Use the 'url' field (e.g., /media/file.webp) to display the image to the user. Use 'saved_as' if you need to delete it later."
    },
    {
      "name": "media_delete",
      "schema": {
        "method": "DELETE",
        "path": "/media/{filename}",
        "params": { "filename": "string" },
        "auth": True,
        "returns": {
          "status": "string",
          "filename": "string"
        }
      },
      "type": "media",
      "description": "Delete an uploaded media file. Requires the clean filename (without /media/ prefix)."
    },
    {
      "name": "media_list",
      "schema": {
        "method": "GET",
        "path": "/media",
        "params": {},
        "returns": {
          "images": "List[{ 'filename': string, 'url': string }]"
        }
      },
      "type": "media",
      "description": "List all available images. Returns objects containing 'filename' (for deletion) and 'url' (relative path for display)."
    },
    {
      "name": "file_get",
      "schema": {
        "method": "GET",
        "path": "/file/{filename}",
        "params": { "filename": "string" }
      },
      "type": "media",
      "description": "Retrieve arbitrary uploaded file"
    },
    {
      "name": "file_upload",
      "schema": {
        "method": "POST",
        "path": "/file",
        "body": {
          "file": "UploadFile"
        },
        "auth": True
      },
      "type": "media",
      "description": "Upload arbitrary file"
    },
    {
      "name": "blog_list",
      "schema": {
        "method": "GET",
        "path": "/api/blog",
        "returns": {
          "type": "List[Object]",
          "items": {
            "slug": "string - The unique identifier for the blog post.",
            "title": "string - The title of the blog post.",
            "content": "string - A summary of the blog post's content.",
            "tags": "List[string] - A list of tags associated with the post.",
            "thumb": "string - URL or path to the post's thumbnail image.",
            "type": "string - The type of the page (e.g., 'sys:blog').",
            "created": "string - The creation date of the post (ISO format).",
            "updated": "string - The last updated date of the post (ISO format).",
            "author": "string - The name of the post's author."
          }
        }
      },
      "type": "blog",
      "description": "List all available blog posts with summary data."
    },
    {
      "name": "blog_get",
      "schema": {
        "method": "GET",
        "path": "/api/blog/{slug}",
        "params": { "slug": "string" },
        "returns": {
          "slug": "string - The unique identifier for the blog post.",
          "title": "string - The title of the blog post.",
          "content": "string - The meta description of the blog post.",
          "markdown": "string - The full content of the post in Markdown format.",
          "html": "string - The full content of the post rendered as HTML.",
          "tags": "List[string] - A list of tags associated with the post.",
          "thumb": "string - URL or path to the post's thumbnail image.",
          "type": "string - The type of the page (e.g., 'sys:blog').",
          "created": "string - The creation date of the post (ISO format).",
          "updated": "string - The last updated date of the post (ISO format).",
          "author": "string - The name of the post's author."
        }
      },
      "type": "blog",
      "description": "Retrieve a single blog page by its slug, including full content."
    }
  ]
}


class ConfigService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Retrieves all settings from the database and reconstructs them into a
        single configuration dictionary.
        """
        return crud.get_all_settings(self.db)

    def get_setting_value(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Retrieves the value for a single setting by its key.

        If the setting is not found in the database, it returns the provided
        default value. This is the primary way other services should
        interact with configuration.
        """
        value = crud.get_setting(self.db, key=key)
        
        # If the value is not in the DB, fall back to the hardcoded default
        if value is None:
            return DEFAULT_CONFIG.get(key, default)
            
        return value

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
        
        if key in ["ai_key", "theme", "system_note", "ai_endpoint"]:
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
            # Run any specific validation rules for the setting key.
            self._validate_setting(key, value)
            
            # Use the CRUD function to save each setting.
            crud.save_setting(self.db, key=key, value=value)
        
        # Return the complete, updated set of all settings.
        return self.get_all_settings()

    def seed_initial_settings(self):
        """
        Seeds the database with the default application configuration if no
        settings currently exist.
        """
        # Check if a core setting already exists. If so, we assume seeding is done.
        if crud.get_setting(self.db, "system_note"):
            return

        print("No settings found in database. Seeding initial application configuration.")
        
        # Iterate through the default config dictionary and save each item
        for key, value in DEFAULT_CONFIG.items():
            crud.save_setting(self.db, key=key, value=value)

        print("✓ Default settings seeded.")