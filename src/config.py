import asyncio
import os
import json
from dataclasses import dataclass, asdict

CONFIG_PATH = "config.json"

@dataclass
class DefaultConfig:
    system_note: str = "You are a friendly AI Assistant, Do as you are instructed to."
    ai_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    base_llm:str= "gemini-2.5-pro-exp-03-25"
    temperature:float = 0.5
    ai_key:str = ""

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

def get_key(path:str = CONFIG_PATH) -> str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = DefaultConfig(**data)
            return current_config.ai_key 
    else:
        return ""
    
def save_config(config: DefaultConfig, path: str = CONFIG_PATH) -> None:
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing_data = json.load(f)
            # Preserve the existing ai_key if the new one is empty
            if not config.ai_key:
                config.ai_key = existing_data.get("ai_key", "")
    with open(path, 'w') as f:
        json.dump(asdict(config), f, indent=2)
