from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Page:
    title: str
    slug: str
    content: Optional[str] = None
    markdown: Optional[str] = None
    html: Optional[str] = None
    url: Optional[str] = None
    content_length: Optional[int] = None
    tags: Optional[List[str]] = None
    thumb: Optional[str] = None
    type: str = "markdown"
    created: Optional[str] = None
    updated: Optional[str] = None
    author: Optional[str] = None
    custom: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Prompt:
    system:str = None
    user:str = None
    assistant:str = None
    model:str = None
    endpoint:str = None
    temp:str = None
    context:str = None
    limit:str = None
    ai_key:str = None
    stop:str = None
    stream:bool = False
