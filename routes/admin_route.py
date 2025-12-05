from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Any, Dict, List, Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime

# Local imports
from src.generator import generate_markdown_page
from src.config import load_or_create_config, save_config
from data import db 
from data.models import Page as PageData
from src.auth import get_current_user, optional_auth, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="static")

# --- DATA MODELS ---

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
    ai_key: Optional[str] = None

# --- HTML VIEW ROUTES (The Unified Dashboard) ---

@router.get("/")
async def view_dashboard(request: Request, user: Optional[dict] = Depends(optional_auth)):
    """
    Main Dashboard. Accessible by ANY logged-in user.
    """
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse("admin/page.html", {
        "request": request,
        "user": user,
        "role": user["role"],
        "display_name": user.get("display_name"),
        "pfp_url": user.get("pfp_url")
    })

@router.get("/page/")
async def view_page_manager(request: Request, user: Optional[dict] = Depends(optional_auth)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse("admin/page.html", {
        "request": request,
        "user": user,
        "role": user["role"]
    })

# --- SENSITIVE HTML VIEWS (Admins Only) ---
# We use require_admin here so normal users can't even see the CONFIG/FILES HTML.

@router.get("/config/")
async def view_config(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse("admin/config.html", {
        "request": request, 
        "user": user,
        "role": user["role"]
    })

@router.get("/forms/")
async def view_forms(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse("admin/form.html", {
        "request": request, 
        "user": user
    })

@router.get("/media/")
async def view_media(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse("admin/media.html", {
        "request": request, 
        "user": user
    })

@router.get("/files/")
async def view_files(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse("admin/file_manager.html", {
        "request": request, 
        "user": user
    })

@router.get("/users/")
async def view_files(request: Request, user: dict = Depends(require_admin)):
    return templates.TemplateResponse("admin/users.html", {
        "request": request, 
        "user": user
    })

# --- API ROUTES (Strictly Secured) ---

@router.post("/api/page/", response_model=PageModel)
def create_page(
    page: PageModel,
    user: dict = Depends(require_admin), # Only Admins can create pages
):
    if db.get_page(page.slug):
        raise HTTPException(status_code=400, detail="Page already exists")
   
    page_data = page.dict()
    now = datetime.now().isoformat()
    page_data['created'] = now
    page_data['updated'] = now
    # FIX: Token uses 'sub', not 'username'
    page_data['author'] = user.get('sub') 
    page_data["custom"] = page_data.get("custom", {})
    
    db.add_page(PageData(**page_data))
    return PageModel(**page_data)

@router.get("/api/page/list/", response_model=List[PageModel])
def list_pages(user: dict = Depends(require_admin)):
    # ALLOW all logged in users to see the list (for the dashboard)
    # If you want only admins to see the list, change to Depends(require_admin)
    return db.list_pages()

@router.delete("/api/page/{slug}/")
def delete_page(slug: str, user: dict = Depends(require_admin)):
    if not db.get_page(slug):
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete_page(slug)
    return {"message": "Page deleted successfully"}

@router.get("/api/page/{slug}/", response_model=PageModel)
def read_page(slug: str, user: dict = Depends(get_current_user)):
    # Allow editors/users to read page data to view it
    page = db.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.put("/api/page/{slug}/", response_model=PageModel)
def update_page(slug: str, page: PageModel, user: dict = Depends(require_admin)):
    existing_page = db.get_page(slug)
    if not existing_page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    page_data = page.dict()
    page_data['updated'] = datetime.now().isoformat()
    page_data['created'] = existing_page.created
    page_data['author'] = existing_page.author
    page_data["custom"] = page_data.get("custom", existing_page.custom or {})
    
    db.update_page(PageData(**page_data))
    return PageModel(**page_data)

@router.get("/api/config/", response_model=ConfigModel)
def get_config(user: dict = Depends(require_admin)):
    config = load_or_create_config()
    return ConfigModel(
        system_note=config.system_note,
        ai_endpoint=config.ai_endpoint,
        base_llm=config.base_llm,
        temperature=config.temperature
    )

@router.post("/api/config/", response_model=ConfigModel)
def update_config(updated: ConfigModel, user: dict = Depends(require_admin)):
    config = load_or_create_config()
    config.system_note = updated.system_note
    config.ai_endpoint = updated.ai_endpoint
    config.base_llm = updated.base_llm
    config.temperature = updated.temperature

    if updated.ai_key is not None:
        config.ai_key = updated.ai_key

    save_config(config)
    return updated

# --- CUSTOM DYNAMIC ADMIN PAGES ---

@router.get("/{slug}/", response_class=HTMLResponse)
async def serve_custom_admin_page(slug: str, user: dict = Depends(require_admin)):
    # Only admins can access custom admin tools defined in pages
    page = db.get_page(slug)

    if not page or not (page.tags and 'admin' in page.tags):
        raise HTTPException(status_code=404, detail="Admin tool not found")

    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)

    generated = generate_markdown_page(page.title, page.markdown)
    return HTMLResponse(content=generated, status_code=200)