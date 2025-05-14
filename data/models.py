from dataclasses import dataclass
from typing import List, Optional


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