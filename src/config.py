import asyncio
import os
import json
from dataclasses import dataclass, asdict

CONFIG_PATH = "config.json"

@dataclass
class DefaultConfig:
    system_note: str = "ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. Also, try to ellaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE"
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
    with open(path, 'w') as f:
        json.dump(asdict(config), f, indent=2)
