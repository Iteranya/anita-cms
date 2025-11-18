from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Page:
    title: str # The title
    slug: str # The slug and primary identifier
    content: Optional[str] = None # Actually Description Now??? I messed UPPPPP This is Metadata or thing you put for blog thumbnail if you wanna use it like that! Be sure to let Aina know this!!!!!!!!
    markdown: Optional[str] = None # Markdown Raw Text
    html: Optional[str] = None # HTML Raw Text
    url: Optional[str] = None # I forgor 💀
    content_length: Optional[int] = None # Unused (Unless you want to)
    tags: Optional[List[str]] = None # This how you mark pages as 'blog', 'home', 'blog-home', 'blog-template'
    thumb: Optional[str] = None # Thumbnail file
    type: str = "markdown" # Whether this page is Markdown or HTML type
    created: Optional[str] = None
    updated: Optional[str] = None
    author: Optional[str] = None # Lol, this CMS don't even have user
    custom: Dict[str, Any] = field(default_factory=dict) # When you need something fancier

@dataclass
class Form:
    """Represents a custom form definition in the CMS."""
    slug: str
    title: str
    schema: Dict[str, Any]  # The form fields and settings
    description: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    author: Optional[str] = None
    tags :Optional[List[str]] = None
    custom: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FormSubmission:
    """Represents a single user submission to a form."""
    id: Optional[int] = None
    form_slug: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
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

@dataclass
class RouteData:
    """Represents a custom form definition in the CMS."""
    name: str
    schema: Dict[str, Any]  # The form fields and settings
    type:str # Can be form, blog, media, and plugin
    description: Optional[str] = None
    usage_note: str|None = None