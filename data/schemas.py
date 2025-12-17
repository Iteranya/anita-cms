import nh3
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional, Dict, Any

# --- Sanitization Utilities ---

def sanitize_text(v: Any) -> Any:
    """
    Strips all HTML tags and attributes from a string using nh3.
    This is the direct replacement for the old bleach-based function.
    """
    if isinstance(v, str):
        return nh3.clean(v, tags=set(), attributes={}, strip_comments=True).strip()
    return v

def sanitize_recursively(value: Any) -> Any:
    """
    Recursively traverses a dictionary or list and applies sanitize_text to all strings.
    """
    if isinstance(value, str):
        return sanitize_text(value)
    
    if isinstance(value, list):
        return [sanitize_recursively(item) for item in value]
    
    if isinstance(value, dict):
        return {
            sanitize_text(key) if isinstance(key, str) else key: sanitize_recursively(val) 
            for key, val in value.items()
        }
        
    return value

# --- Tag Flattening Utility (with Sanitization) ---

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
    content: Optional[str] = None # THIS IS JUST DESCRIPTION, page 'content' is inside markdown/html, this contains only short description, like, a sentence or two
    markdown: Optional[str] = None # Bleached Until Per-Page CSP Configuration Is Implemented
    html: Optional[str] = None  # EXEMPTED
    tags: Optional[List[str]] = []
    thumb: Optional[str] = None
    type: Optional[str] = "page"
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}
    
    @field_validator('title', 'content', 'markdown', 'author', 'thumb', 'type', mode='before')
    @classmethod
    def bleach_text_fields(cls, v):
        return sanitize_text(v)

    @field_validator('custom', mode='before')
    @classmethod
    def bleach_custom_dict(cls, v):
        return sanitize_recursively(v)

class PageCreate(PageBase):
    slug: str
    html: None = Field(default=None, exclude=True)
    markdown: None = Field(default=None, exclude=True)
    @field_validator('slug', mode='before')
    @classmethod
    def bleach_slug(cls, v): return sanitize_text(v)

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
    html: str
    custom: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    @field_validator('custom', mode='before')
    @classmethod
    def bleach_custom_dict(cls, v): return sanitize_recursively(v)
    model_config = ConfigDict(extra="ignore")

class PageMarkdownUpdate(BaseModel):
    markdown: str
    custom: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    @field_validator('markdown', mode='before')
    @classmethod
    def bleach_markdown(cls, v): return sanitize_text(v)
    @field_validator('custom', mode='before')
    @classmethod
    def bleach_custom_dict(cls, v): return sanitize_recursively(v)
    model_config = ConfigDict(extra="ignore")

class PageData(Page):
    # Overwrite these fields to exclude them from the JSON response
    html: Optional[str] = Field(default=None, exclude=True)
    markdown: Optional[str] = Field(default=None, exclude=True)


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
    def bleach_dict_fields(cls, v): return sanitize_recursively(v)

class FormCreate(FormBase):
    slug: str
    @field_validator('slug', mode='before')
    @classmethod
    def bleach_slug(cls, v): return sanitize_text(v)

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

class SubmissionBase(BaseModel):
    data: Dict[str, Any]
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    @field_validator('author', mode='before')
    @classmethod
    def bleach_author(cls, v): return sanitize_text(v)
    
    # This now properly sanitizes the main submission vectors
    @field_validator('data', 'custom', mode='before')
    @classmethod
    def bleach_submission_dicts(cls, v):
        return sanitize_recursively(v)

class SubmissionCreate(SubmissionBase):
    form_slug: str
    @field_validator('form_slug', mode='before')
    @classmethod
    def bleach_slug(cls, v): return sanitize_text(v)

class SubmissionUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    custom: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    @field_validator('data', 'custom', mode='before')
    @classmethod
    def bleach_submission_dicts(cls, v):
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
    def bleach_user_dicts(cls, v): return sanitize_recursively(v)

class UserCreate(UserBase):
    username: str
    hashed_password: str
    @field_validator('username', mode='before')
    @classmethod
    def bleach_username(cls, v): return sanitize_text(v)

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
    def bleach_username(cls, v): return sanitize_text(v)

# --- Setting Schemas ---

class SettingBase(BaseModel):
    value: Dict[str, Any]
    @field_validator('value', mode='before')
    @classmethod
    def bleach_value_dict(cls, v): return sanitize_recursively(v)

class SettingCreate(SettingBase):
    key: str
    @field_validator('key', mode='before')
    @classmethod
    def bleach_key(cls, v): return sanitize_text(v)

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

# --- AI & Tooling Schemas ---

class Prompt(BaseModel):
    system: Optional[str] = None
    user: Optional[str] = None
    assistant: Optional[str] = None 
    model: Optional[str] = None
    temp: Optional[float] = None
    endpoint: Optional[str] = None
    ai_key: Optional[str] = None
    stop: Optional[List[str]] = None
    result: Optional[str] = None

class RouteData(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    usage_note: Optional[str] = None
    @field_validator('schema', mode='before')
    @classmethod
    def bleach_schema_dict(cls, v): return sanitize_recursively(v)

class MarkdownEditRequest(BaseModel):
    global_instruction: str
    edit_instruction: str
    editor_content: str
    selected_text: str
    @field_validator('*', mode='before')
    @classmethod
    def bleach_all_fields(cls, v: Any) -> Any: return sanitize_text(v)

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