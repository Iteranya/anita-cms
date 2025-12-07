# file: config.py

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

# Import the new database module for persistence
from data import database
from data.models import RouteData

# -----------------------
# Data Models (Unchanged)
# -----------------------

@dataclass
class DefaultConfig:
    system_note: str = "You are a friendly AI Assistant, Do as you are instructed to."
    ai_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    base_llm: str = "gemini-2.5-pro-exp-03-25"
    temperature: float = 0.5
    ai_key: str = ""
    theme: str = "default"
    routes: List[RouteData] = None

    def __post_init__(self):
        if self.routes is None:
            self.routes = []

@dataclass
class MailConfig:
    server_email: str = "onboarding@resend.dev"
    target_email: str = ""
    header: str = ""
    footer: str = ""
    api_key: str = ""

# -----------------------
# File Paths (REMOVED)
# No longer needed as we use the database.
# -----------------------

# -----------------------
# Load Functions (Refactored for Database)
# -----------------------

def load_or_create_config() -> DefaultConfig:
    """Loads the main configuration from the database, or creates it if it doesn't exist."""
    data = database.get_setting("main_config")

    if data:
        # Deserialize routes into RouteData objects
        raw_routes = data.get("routes", [])
        data["routes"] = [RouteData(**route) for route in raw_routes]

        config = DefaultConfig(**data)

        # "Duct Tape Security": Always clear the key on a general load
        # to prevent it from being accidentally exposed to the client.
        config.ai_key = ""
        return config

    # If no config in DB, create one from scratch
    print("No main config found in database. Creating a default one.")
    default_config = DefaultConfig()
    save_config(default_config)
    
    # Clear key after saving before returning
    default_config.ai_key = ""
    return default_config

def load_or_create_mail_config() -> MailConfig:
    """Loads the mail configuration from the database, or creates it if it doesn't exist."""
    data = database.get_setting("mail_config")

    if data:
        return MailConfig(**data)

    print("No mail config found in database. Creating a default one.")
    mail_config = MailConfig()
    save_mail_config(mail_config)
    return mail_config

# -----------------------
# Getter Helpers (Refactored for Database)
# -----------------------

def get_key() -> str:
    """Securely retrieves just the AI key from the database."""
    data = database.get_setting("main_config")
    return data.get("ai_key", "") if data else ""

def get_theme() -> str:
    """Retrieves just the theme name from the database."""
    data = database.get_setting("main_config")
    return data.get("theme", "default") if data else "default"

# -----------------------
# Save Functions (Refactored for Database)
# -----------------------

def save_config(config: DefaultConfig) -> None:
    """Saves the main configuration to the database."""
    # Preserve existing ai_key if the new config has an empty one
    if not config.ai_key:
        existing_key = get_key() # Use our secure getter
        if existing_key:
            config.ai_key = existing_key

    # Convert the dataclass object to a dictionary for JSON serialization
    serialized_data = asdict(config)
    
    # Ensure nested RouteData objects also become dictionaries
    serialized_data["routes"] = [asdict(r) for r in config.routes]

    database.save_setting("main_config", serialized_data)

def save_mail_config(config: MailConfig) -> None:
    """Saves the mail configuration to the database."""
    # Preserve existing api_key
    if not config.api_key:
        existing_data = database.get_setting("mail_config")
        if existing_data and existing_data.get("api_key"):
            config.api_key = existing_data["api_key"]

    database.save_setting("mail_config", asdict(config))