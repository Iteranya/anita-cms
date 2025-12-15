# file: data/schemas.py

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional, Dict, Any

# --- Utility ---

def flatten_tags_to_strings(v: Any) -> List[str]: # Legacy but useful
    """
    Converts a list of Tag objects -> ['<cat>', '<dog>']
    Also strips the brackets for cleaner API output: 'cat', 'dog'
    """
    if not v:
        return []
        
    # Case 1: Already a list of strings (e.g. from client input)
    # Note: We must check for an empty list first to avoid index errors on v[0]
    if isinstance(v[0], str):
        return [t.replace("<", "").replace(">", "") for t in v]
        
    # Case 2: It's a list of SQLAlchemy Tag objects from the database.
    # We check for the .name attribute as a safe way to identify these objects.
    if hasattr(v[0], 'name'):
        return [tag.name.replace("<", "").replace(">", "") for tag in v]

    # Fallback if the data is in an unexpected format
    return v


# --- Page Schemas ---

class PageBase(BaseModel):
    title: str
    content: Optional[str] = None
    markdown: Optional[str] = None
    html: Optional[str] = None
    tags: Optional[List[str]] = []
    thumb: Optional[str] = None
    type: Optional[str] = "page"
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}

class PageCreate(PageBase):
    slug: str

class PageUpdate(PageBase):
    # All fields are optional for updating
    title: Optional[str] = None

class Page(PageBase):
    slug: str
    created: str
    updated: str

    @field_validator('tags', mode='before')
    @classmethod
    def clean_tags_output(cls, v):
        return flatten_tags_to_strings(v)

    model_config = ConfigDict(from_attributes=True)

# --- Form Schemas ---

class FormBase(BaseModel):
    title: str
    # The API field is 'schema'. Pydantic will populate it from the ORM attribute 'schema'.
    # CHANGE: Use `alias` so it works for both input and output serialization.
    schema: Dict[str, Any] = Field(alias='schema') 
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    custom: Optional[Dict[str, Any]] = {}
    author: Optional[str] = None

class FormCreate(FormBase):
    slug: str

class FormUpdate(FormBase):
    # All fields are optional for updating
    title: Optional[str] = None
    # We redefine `schema` here to make it optional for updates
    # CHANGE: Use `alias` here as well.
    schema: Optional[Dict[str, Any]] = Field(default=None, alias='schema')


class Form(FormBase):
    id: int
    slug: str
    created: str
    updated: str
    # <--- NEW: Add the same tag validator here
    @field_validator('tags', mode='before')
    @classmethod
    def clean_tags_output(cls, v):
        return flatten_tags_to_strings(v)
    
    model_config = ConfigDict(from_attributes=True)

# --- Submission Schemas ---

class SubmissionBase(BaseModel):
    data: Dict[str, Any]
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []  

class SubmissionCreate(SubmissionBase):
    form_slug: str

class SubmissionUpdate(BaseModel):
    # Only allow updating data, custom fields, and tags
    data: Optional[Dict[str, Any]] = None
    custom: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None 


class Submission(SubmissionBase):
    id: int
    form_slug: str
    created: str
    updated: str

    @field_validator('tags', mode='before')
    @classmethod
    def clean_tags_output(cls, v):
        return flatten_tags_to_strings(v)

    model_config = ConfigDict(from_attributes=True)

# --- User Schemas ---

class UserBase(BaseModel):
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    role: str = "viewer"
    disabled: bool = False
    settings: Optional[dict] = None
    custom: Optional[dict] = None

class UserCreate(UserBase):
    username: str
    hashed_password: str

class UserUpdate(UserBase):
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    role: Optional[str] = None
    disabled: Optional[bool] = None
    settings: Optional[dict] = None
    custom: Optional[dict] = None

class User(UserBase):
    """The User model returned by the API (never includes the password)."""
    username: str
    
    class Config:
        from_attributes=True

class CurrentUser(BaseModel):
    """Schema representing the data decoded from the JWT access token."""
    username: str
    role: str
    display_name: Optional[str] = None
    exp: int

# --- Setting Schemas ---

class SettingBase(BaseModel):
    value: Dict[str, Any]

class SettingCreate(SettingBase):
    key: str

class Setting(SettingCreate):
    class Config:
        from_attributes=True

# --- Role Schemas ---

class RoleBase(BaseModel):
    permissions: List[str]

class RoleCreate(RoleBase):
    role_name: str

class Role(RoleCreate):
    class Config:
        from_attributes=True

class UserCreateWithPassword(UserBase):
    """Schema used for creating a user via the API, accepts plain password."""
    username: str
    password: str
    role:str
    display_name:str

class Prompt(BaseModel):
    # Core content
    system: Optional[str] = None
    user: Optional[str] = None
    assistant: Optional[str] = None 

    # Overrides for default settings
    model: Optional[str] = None
    temp: Optional[float] = None
    endpoint: Optional[str] = None
    ai_key: Optional[str] = None
    stop: Optional[List[str]] = None

    # Field to store the final result
    result: Optional[str] = None

class RouteData(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    usage_note: Optional[str] = None

class MarkdownEditRequest(BaseModel):
    global_instruction: str
    edit_instruction: str
    editor_content: str
    selected_text: str

class MediaFile(BaseModel):
    """Represents a single media file available on the server."""
    filename: str  # The actual name of the file on disk (e.g., my-image_12345.webp)
    url: str       # The relative URL to access the file (e.g., /media/my-image_12345.webp)

class UploadedFileReport(BaseModel):
    """Reports the result of a single file upload attempt."""
    original: str
    saved_as: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    format_chosen: Optional[str] = None
    error: Optional[str] = None

class UploadResult(BaseModel):
    """The final response after an upload operation."""
    status: str
    total: int
    files: List[UploadedFileReport]



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
    # Can be used for both tags and forms
    name: str  # for tags
    slug: str | None = None # for forms
    count: int

class DashboardActivity(BaseModel):
    top_forms_by_submission: List[DashboardActivityItem]
    top_tags_on_pages: List[DashboardActivityItem]

class DashboardRecentItems(BaseModel):
    newest_pages: List[Page] # Assumes you have a 'Page' Pydantic schema
    latest_updates: List[Page]
    latest_submissions: List[Submission] # Assumes you have a 'Submission' schema

class DashboardStats(BaseModel):
    """The complete response model for the dashboard statistics endpoint."""
    core_counts: DashboardCoreCounts
    page_stats: DashboardPageStats
    activity: DashboardActivity
    recent_items: DashboardRecentItems

    class Config:
        from_attributes = True 