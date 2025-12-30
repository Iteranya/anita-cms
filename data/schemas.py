from dataclasses import dataclass
import nh3
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional, Dict, Any

# Look, I know, I know, Jinja and Alpine's x-text auto escapes things
# But I don't care

# --- Regex Constants ---

# Lowercase, alphanumeric, dashes, and underscore only. No spaces.
SLUG_PATTERN = re.compile(r'^[a-z0-9-_]+$')

# --- Sanitization Utilities ---

def validate_slug_format(v: Any) -> str:
    """
    Strict validation for slugs and dict keys. 
    Only allows lowercase a-z, 0-9, and dashes.
    """
    if not isinstance(v, str):
        return v
    
    # If empty string is allowed, handle it, otherwise strict check
    if len(v) > 0 and not SLUG_PATTERN.match(v):
        raise ValueError(f"Invalid format: '{v}'. Must be lowercase, alphanumeric, and dashes only (no spaces).")
    
    return v

def sanitize_text(v: Any) -> Any:
    """
    Strips all HTML tags and attributes from a string using nh3.
    """
    if isinstance(v, str):
        return nh3.clean(v, tags=set(), attributes={}, strip_comments=True).strip()
    return v

def sanitize_recursively(value: Any) -> Any:
    """
    Recursively traverses a dictionary or list.
    1. Values (Strings) -> Sanitized via nh3.
    2. Keys (Strings) -> Validated as Slugs (Strict regex).
    """
    if isinstance(value, str):
        return sanitize_text(value)
    
    if isinstance(value, list):
        return [sanitize_recursively(item) for item in value]
    
    if isinstance(value, dict):
        new_dict = {}
        for key, val in value.items():
            # Validate Key (Strict Slug) - Do not bleach, just validate
            if isinstance(key, str):
                validate_slug_format(key)
            
            # Recurse on Value
            new_dict[key] = sanitize_recursively(val)
        return new_dict
        
    return value

# --- Tag Flattening Utility ---

def flatten_tags_to_strings(v: Any) -> List[str]:
    """Converts Tag objects, sanitizes, and cleans for API output."""
    if not v: 
        return []
    if isinstance(v[0], str):
        return [sanitize_text(t).replace("<", "").replace(">", "") for t in v]
    if hasattr(v[0], 'name'):
        return [sanitize_text(tag.name).replace("<", "").replace(">", "") for tag in v]
    return v


# --- Page Schemas ---

class PageBase(BaseModel):
    title: str
    content: Optional[str] = None # Short description only, not actual page content
    markdown: Optional[str] = None # Sanitized Until Per-Page CSP is Implemented
    html: Optional[str] = None  # EXEMPTED / UNTOUCHED / LITERALLY THE ENTIRE SITE
    tags: Optional[List[str]] = []
    thumb: Optional[str] = None
    type: Optional[str] = "markdown"
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {} # Exempted These Are For Aina/Asta To Use
    
    @field_validator('title', 'content', 'markdown', 'author', 'thumb', 'type', mode='before')
    @classmethod
    def bleach_text_fields(cls, v):
        return sanitize_text(v)

class PageCreate(PageBase):
    slug: str
    html: None = Field(default=None, exclude=True)
    markdown: None = Field(default=None, exclude=True)

    @field_validator('slug', mode='before')
    @classmethod
    def validate_slug(cls, v): 
        return validate_slug_format(v)

class PageUpdate(PageBase):
    title: Optional[str] = None
    html: None = Field(default=None, exclude=True)
    markdown: None = Field(default=None, exclude=True)
    model_config = ConfigDict(extra="ignore")

class Page(PageBase):
    slug: str
    created: str
    updated: str
    @field_validator('tags', mode='before')
    @classmethod
    def clean_tags_output(cls, v): return flatten_tags_to_strings(v)
    model_config = ConfigDict(from_attributes=True)

class PageUpdateHTML(BaseModel):
    html: Optional[str] = None
    custom: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class PageMarkdownUpdate(BaseModel):
    markdown: str
    custom: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    @field_validator('markdown', mode='before')
    @classmethod
    def bleach_markdown(cls, v): return sanitize_text(v)

    @field_validator('custom', mode='before')
    @classmethod
    def validate_and_bleach_dict(cls, v): return sanitize_recursively(v)
    
    model_config = ConfigDict(extra="ignore")

class PageData(Page):
    # Overwrite these fields to exclude them from the JSON response
    html: Optional[str] = Field(default=None, exclude=True)
    markdown: Optional[str] = Field(default=None, exclude=True)

class PageSeed(PageBase):
    slug: str
    @field_validator('slug', mode='before')
    @classmethod
    def validate_slug(cls, v): return validate_slug_format(v)


# --- Form Schemas ---

class FormBase(BaseModel):
    title: str
    schema: Dict[str, Any] = Field(alias='schema') 
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    custom: Optional[Dict[str, Any]] = {}
    author: Optional[str] = None

    @field_validator('title', 'description', 'author', mode='before')
    @classmethod
    def bleach_form_fields(cls, v): return sanitize_text(v)

    @field_validator('custom', 'schema', mode='before')
    @classmethod
    def validate_and_bleach_dicts(cls, v): return sanitize_recursively(v)

class FormCreate(FormBase):
    slug: str
    @field_validator('slug', mode='before')
    @classmethod
    def validate_slug(cls, v): return validate_slug_format(v)

class FormUpdate(FormBase):
    title: Optional[str] = None
    schema: Optional[Dict[str, Any]] = Field(default=None, alias='schema')

class Form(FormBase):
    id: int
    slug: str
    created: str
    updated: str
    @field_validator('tags', mode='before')
    @classmethod
    def clean_tags_output(cls, v): return flatten_tags_to_strings(v)
    model_config = ConfigDict(from_attributes=True)


# --- Submission Schemas ---

class SubmissionBase(BaseModel): # Bleach Everything Until Whitelist is Implemented
    data: Dict[str, Any]
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    
    @field_validator('author', mode='before')
    @classmethod
    def bleach_author(cls, v): return sanitize_text(v)
    
    # Validates keys as slugs, recurses and bleaches values
    @field_validator('data', 'custom', mode='before')
    @classmethod
    def validate_and_bleach_dicts(cls, v):
        return sanitize_recursively(v)

class SubmissionCreate(SubmissionBase):
    form_slug: str
    @field_validator('form_slug', mode='before')
    @classmethod
    def validate_slug(cls, v): return validate_slug_format(v)

class SubmissionUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    custom: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    @field_validator('data', 'custom', mode='before')
    @classmethod
    def validate_and_bleach_dicts(cls, v):
        return sanitize_recursively(v)
    
class Submission(SubmissionBase):
    id: int
    form_slug: str
    created: str
    updated: str
    @field_validator('tags', mode='before')
    @classmethod
    def clean_tags_output(cls, v): return flatten_tags_to_strings(v)
    model_config = ConfigDict(from_attributes=True)


# --- User Schemas ---

class UserBase(BaseModel):
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    role: str = "viewer"
    disabled: bool = False
    settings: Optional[dict] = None
    custom: Optional[dict] = None
    
    @field_validator('display_name', 'role', mode='before')
    @classmethod
    def bleach_user_text_fields(cls, v): return sanitize_text(v)

    @field_validator('settings', 'custom', mode='before')
    @classmethod
    def validate_and_bleach_dicts(cls, v): return sanitize_recursively(v)

class UserCreate(UserBase):
    username: str
    hashed_password: str
    
    @field_validator('username', mode='before')
    @classmethod
    def validate_username_slug(cls, v): return validate_slug_format(v)

class UserUpdate(UserBase):
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    role: Optional[str] = None
    disabled: Optional[bool] = None
    settings: Optional[dict] = None
    custom: Optional[dict] = None

class MeUpdate(UserBase):
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    settings: Optional[dict] = None
    custom: Optional[dict] = None

class User(UserBase):
    username: str
    class Config: 
        from_attributes = True

class CurrentUser(BaseModel):
    username: str
    role: str
    display_name: Optional[str] = None
    exp: int

class UserCreateWithPassword(UserBase):
    username: str
    password: str
    role: str
    display_name: str
    @field_validator('username', mode='before')
    @classmethod
    def validate_username_slug(cls, v): return validate_slug_format(v)

# --- Setting Schemas ---

class SettingBase(BaseModel):
    value: Dict[str, Any]
    @field_validator('value', mode='before')
    @classmethod
    def validate_and_bleach_value(cls, v): return sanitize_recursively(v)

class SettingCreate(SettingBase):
    key: str
    @field_validator('key', mode='before')
    @classmethod
    def validate_key_slug(cls, v): return validate_slug_format(v)

class Setting(SettingCreate):
    class Config: 
        from_attributes = True

# --- Role Schemas ---

class RoleBase(BaseModel):
    permissions: List[str]

class RoleCreate(RoleBase):
    role_name: str
    @field_validator('role_name', mode='before')
    @classmethod
    def bleach_role_name(cls, v): return sanitize_text(v)

class Role(RoleCreate):
    class Config: 
        from_attributes = True

# --- Media Schemas ---

class MediaFile(BaseModel):
    filename: str
    url: str

class UploadedFileReport(BaseModel):
    original: str
    saved_as: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    format_chosen: Optional[str] = None
    error: Optional[str] = None

class UploadResult(BaseModel):
    status: str
    total: int
    files: List[UploadedFileReport]

# --- Dashboard Schemas (Output only, no validation needed) ---

class DashboardCoreCounts(BaseModel):
    pages: int
    forms: int
    submissions: int
    users: int
    tags: int

class DashboardPageStats(BaseModel):
    public_count: int
    blog_posts_count: int

class DashboardActivityItem(BaseModel):
    name: str
    slug: str | None = None
    count: int

class DashboardActivity(BaseModel):
    top_forms_by_submission: List[DashboardActivityItem]
    top_tags_on_pages: List[DashboardActivityItem]

class DashboardRecentItems(BaseModel):
    newest_pages: List[Page]
    latest_updates: List[Page]
    latest_submissions: List[Submission]

class DashboardStats(BaseModel):
    core_counts: DashboardCoreCounts
    page_stats: DashboardPageStats
    activity: DashboardActivity
    recent_items: DashboardRecentItems
    class Config:
        from_attributes = True

# --- Internal Use Schemas Untouched By Frontend No Need For Cleaning Here ---

@dataclass
class AlpineData:
    slug:str # The Slug
    name:str # Friendly Name
    description:str | None # Description and usage note
    category:str # Category
    data:str # String containing alpine data snippet

@dataclass
class EmbedData:
    slug:str # The Slug
    name:str # Friendly Name
    description:str | None # Description and usage note
    category:str # Category
    data:str # String containing embed data snippet

# WHY IS IT IDENTICAL!?!?!