from __future__ import annotations
import asyncio
import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from data.models import RouteData

# -----------------------
# Data Models
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
# File Paths
# -----------------------

CONFIG_PATH = "config.json"
MAIL_CONFIG_PATH = "mail_config.json"


# -----------------------
# Load Functions
# -----------------------

def load_or_create_config(path: str = CONFIG_PATH) -> DefaultConfig:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)

        # Deserialize routes into RouteData objects
        raw_routes = data.get("routes", [])
        data["routes"] = [RouteData(**route) for route in raw_routes]

        config = DefaultConfig(**data)

        # Duct Tape Security
        config.ai_key = ""
        return config

    # Create default if missing
    default_config = DefaultConfig()
    save_config(default_config, path)
    print(f"No config found. Created default at {path}.")
    return default_config


def load_or_create_mail_config(path: str = MAIL_CONFIG_PATH) -> MailConfig:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            return MailConfig(**data)

    mail_config = MailConfig()
    save_mail_config(mail_config, path)
    print(f"No mail config found. Created default at {path}.")
    return mail_config


# -----------------------
# Getter Helpers
# -----------------------

def get_key(path: str = CONFIG_PATH) -> str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get("ai_key", "")
    return ""


def get_theme(path: str = CONFIG_PATH) -> str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get("theme", "default")
    return "default"


# -----------------------
# Save Functions
# -----------------------

def save_config(config: DefaultConfig, path: str = CONFIG_PATH) -> None:
    # Preserve existing ai_key if new config has empty key
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing = json.load(f)
            if not config.ai_key:
                config.ai_key = existing.get("ai_key", "")

    # Convert for JSON
    serialized = asdict(config)

    # Ensure RouteData objects become dicts
    serialized["routes"] = [asdict(r) for r in config.routes]

    with open(path, 'w') as f:
        json.dump(serialized, f, indent=2)


def save_mail_config(config: MailConfig, path: str = MAIL_CONFIG_PATH) -> None:
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing = json.load(f)
            if not config.api_key:
                config.api_key = existing.get("api_key", "")

    with open(path, 'w') as f:
        json.dump(asdict(config), f, indent=2)
