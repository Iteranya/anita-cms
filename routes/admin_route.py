from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any, Dict, List, Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.generator import generate_markdown_page
from src.config import load_or_create_config, save_config, load_or_create_mail_config, save_mail_config
from data import db  # Import the db module with standalone functions
from data.models import Page as PageData
from src.auth import get_current_user, optional_auth
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])

class PageModel(BaseModel):
    title: str
    slug: str
    content: Optional[str] = None
    markdown: Optional[str] = None
    html: Optional[str] = None
    tags: Optional[List[str]] = None
    thumb: Optional[str] = None
    type: str = "markdown"
    created: Optional[str] = None
    updated: Optional[str] = None
    author: Optional[str] = None
    custom: Optional[Dict[str, Any]] = {}

class ConfigModel(BaseModel):
    system_note: str
    ai_endpoint: str
    base_llm: str
    temperature: float
    ai_key: Optional[str] = None  # Accept in POST, but don't expose in GET

class MailModel(BaseModel):
    server_email:str
    target_email:str
    header:Optional[str] = ""
    footer:Optional[str] = ""
    api_key:Optional[str] = None

templates = Jinja2Templates(directory="static")

@router.get("/old", response_class=HTMLResponse)
async def get_html(request: Request, user: Optional[str] = Depends(optional_auth)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    template_path = "static/admin/index_old.html"
    with open(template_path, "r") as f:
        html = f.read()

    return html

@router.get("/")
async def admin_panel(request: Request,  user: Optional[str] = Depends(optional_auth)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse("admin/index.html", {"request": request})

@router.post("/api/", response_model=PageModel)
def create_page(
    page: PageModel,
    user: dict = Depends(get_current_user),  # Enforces authentication
):
    if db.get_page(page.slug):
        raise HTTPException(status_code=400, detail="Page already exists")
   
    # Add timestamps and author
    page_data = page.dict()
    now = datetime.now().isoformat()
    page_data['created'] = now
    page_data['updated'] = now
    page_data['author'] = user.get('username')  # Use whatever user identifier you have
    page_data["custom"] = page_data.get("custom", {})
    
    db.add_page(PageData(**page_data))
    return PageModel(**page_data)

@router.get("/api/{slug}/", response_model=PageModel)
def read_page(slug: str, user: dict = Depends(get_current_user)):
    page = db.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.put("/api/{slug}/", response_model=PageModel)
def update_page(slug: str, page: PageModel, user: dict = Depends(get_current_user)):
    print("Received data:", page.dict())
    existing_page = db.get_page(slug)
    if not existing_page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Update timestamp and preserve original author/created
    page_data = page.dict()
    page_data['updated'] = datetime.now().isoformat()
    page_data['created'] = existing_page.created  # Preserve original creation time
    page_data['author'] = existing_page.author    # Preserve original author
    page_data["custom"] = page_data.get("custom", existing_page.custom or {})

    
    db.update_page(PageData(**page_data))
    return PageModel(**page_data)

@router.delete("/api/{slug}/")
def delete_page(slug: str,user: dict = Depends(get_current_user)):
    if not db.get_page(slug):
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete_page(slug)
    return {"message": "Page deleted successfully"}

@router.get("/list/", response_model=List[PageModel])
def list_pages(user: dict = Depends(get_current_user)):
    return db.list_pages()

@router.get("/config/", response_model=ConfigModel)
def get_config(user: dict = Depends(get_current_user)):
    config = load_or_create_config()
    return ConfigModel(
        system_note=config.system_note,
        ai_endpoint=config.ai_endpoint,
        base_llm=config.base_llm,
        temperature=config.temperature
        # Do not include ai_key
    )

@router.post("/config/", response_model=ConfigModel)
def update_config(updated: ConfigModel,user: dict = Depends(get_current_user)):
    config = load_or_create_config()
    config.system_note = updated.system_note
    config.ai_endpoint = updated.ai_endpoint
    config.base_llm = updated.base_llm
    config.temperature = updated.temperature

    if updated.ai_key is not None:
        config.ai_key = updated.ai_key  # Save if provided

    save_config(config)
    return updated

@router.get("/mail/", response_model=MailModel)
def get_config(user: dict = Depends(get_current_user)):
    config = load_or_create_mail_config()
    return MailModel(
    server_email=config.server_email,
    target_email= config.target_email,
    header= config.header,
    footer=config.header,
    api_key=""
    )

@router.post("/mail/", response_model=MailModel)
def update_config(updated: MailModel,user: dict = Depends(get_current_user)):
    config = load_or_create_mail_config()
    config.server_email = updated.server_email
    config.header = updated.header
    config.footer = updated.footer
    config.api_key = updated.api_key
    config.target_email = updated.target_email

    if updated.api_key is not None:
        config.api_key = updated.api_key  # Save if provided

    save_mail_config(config)
    return updated

# Dynamic route to serve 'main' pages
@router.get("/{slug}/", response_class=HTMLResponse)
async def serve_custom_admin_page(slug: str, user: Optional[str] = Depends(optional_auth)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    page = db.get_page(slug)

    # Check if page exists and has the 'main' tag
    if not page or not (page.tags and 'admin' in page.tags):
        raise HTTPException(status_code=404, detail="Main page not found")

    # If it's pure HTML, return as is
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)

    # Otherwise, generate HTML from Markdown
    generated = generate_markdown_page(page.title, page.markdown)
    return HTMLResponse(content=generated, status_code=200)
