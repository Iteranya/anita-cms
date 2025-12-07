# file: data/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
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

    class Config:
        orm_mode = True # Allows Pydantic to read data from ORM models

# --- Form Schemas ---

class FormBase(BaseModel):
    title: str
    # The API will use 'schema', but we map it to 'schema_' for the model
    schema_: Dict[str, Any] = Field(alias='schema')
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    custom: Optional[Dict[str, Any]] = {}
    author: Optional[str] = None

    class Config:
        # This allows using 'schema' in API requests/responses
        allow_population_by_field_name = True

class FormCreate(FormBase):
    slug: str

class FormUpdate(FormBase):
    # All fields are optional for updating
    title: Optional[str] = None
    schema_: Optional[Dict[str, Any]] = Field(alias='schema')

class Form(FormBase):
    id: int
    slug: str
    created: str
    updated: str
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# --- Submission Schemas ---

class SubmissionBase(BaseModel):
    data: Dict[str, Any]
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}

class SubmissionCreate(SubmissionBase):
    form_slug: str

class SubmissionUpdate(BaseModel):
    # Only allow updating data and custom fields
    data: Optional[Dict[str, Any]] = None
    custom: Optional[Dict[str, Any]] = None

class Submission(SubmissionBase):
    id: int
    form_slug: str
    created: str
    updated: str

    class Config:
        orm_mode = True

# --- User Schemas ---

class UserBase(BaseModel):
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    role: str = "user"
    disabled: bool = False

class UserCreate(UserBase):
    username: str
    hashed_password: str

class UserUpdate(UserBase):
    # You might want to have a separate schema for password updates
    display_name: Optional[str] = None
    pfp_url: Optional[str] = None
    role: Optional[str] = None
    disabled: Optional[bool] = None

class User(UserBase):
    """The User model returned by the API (never includes the password)."""
    username: str
    
    class Config:
        orm_mode = True

# --- Setting Schemas ---

class SettingBase(BaseModel):
    value: Dict[str, Any]

class SettingCreate(SettingBase):
    key: str

class Setting(SettingCreate):
    class Config:
        orm_mode = True

# --- Role Schemas ---

class RoleBase(BaseModel):
    permissions: List[str]

class RoleCreate(RoleBase):
    role_name: str

class Role(RoleCreate):
    class Config:
        orm_mode = True

class UserCreateWithPassword(UserBase):
    """Schema used for creating a user via the API, accepts plain password."""
    username: str
    password: str

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
    schema_: Optional[Dict[str, Any]] = None
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