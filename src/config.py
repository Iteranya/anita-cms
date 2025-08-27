import asyncio
import os
import json
from dataclasses import dataclass, asdict

CONFIG_PATH = "config.json"
MAIL_CONFIG_PATH = "mail_config.json"

@dataclass
class DefaultConfig:
    system_note: str = "You are a friendly AI Assistant, Do as you are instructed to."
    ai_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    base_llm:str= "gemini-2.5-pro-exp-03-25"
    temperature:float = 0.5
    ai_key:str = ""
    theme:str = "default"

@dataclass
class MailConfig:
    server_email:str="onboarding@resend.dev"
    target_email:str="" 
    header:str = ""
    footer:str = ""
    api_key:str = ""
    

def load_or_create_config(path: str = CONFIG_PATH) -> DefaultConfig:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = DefaultConfig(**data)
            current_config.ai_key = "" # Duct Tape Security... Fix In Production (Or Not, Maybe This Is Actually Secure Enough :v)
        return current_config
    else:
        default_config = DefaultConfig()
        save_config(default_config, path)
        print(f"No config found. Created default at {path}.")
        default_config.ai_key = ""
        return default_config
    
def load_or_create_mail_config(path: str = MAIL_CONFIG_PATH) -> MailConfig:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = MailConfig(**data)
            return current_config
    else:
        mail_config = MailConfig()
        save_config(mail_config, path)
        print(f"No config found. Created default at {path}.")
        mail_config.api_key = ""
        return mail_config

def get_key(path:str = CONFIG_PATH) -> str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = DefaultConfig(**data)
            return current_config.ai_key 
    else:
        return ""
    
def get_theme(path:str = CONFIG_PATH) ->str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = DefaultConfig(**data)
            return current_config.theme 
    else:
        return "default"
    
def save_config(config: DefaultConfig, path: str = CONFIG_PATH) -> None:
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing_data = json.load(f)
            # Preserve the existing ai_key if the new one is empty
            if not config.ai_key:
                config.ai_key = existing_data.get("ai_key", "")
    with open(path, 'w') as f:
        json.dump(asdict(config), f, indent=2)

def save_mail_config(config: MailConfig, path: str = MAIL_CONFIG_PATH) -> None:
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing_data = json.load(f)
            # Preserve the existing ai_key if the new one is empty
            if not config.api_key:
                config.api_key = existing_data.get("api_key", "")
    with open(path, 'w') as f:
        json.dump(asdict(config), f, indent=2)