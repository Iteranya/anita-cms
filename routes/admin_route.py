from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from src.config import load_or_create_config, save_config
from data import db  # Import the db module with standalone functions
from data.models import Page as PageData
from src.auth import optional_auth
router = APIRouter(prefix="/admin", tags=["Admin"])

class PageModel(BaseModel):
    title: str
    slug: str
    content: str | None = None  # Contains stuff content summary for admin panel, like description
    markdown: str | None = None  # Markdown to render if html don't exist
    html: str | None = None  # HTML to render if markdown don't exist
    tags: List[str] | None = None  # List of keywords
    thumb: str | None = None  # Thumbnail link
    type:str = "markdown"

class ConfigModel(BaseModel):
    system_note: str
    ai_endpoint: str
    base_llm: str
    temperature: float
    ai_key: Optional[str] = None  # Accept in POST, but don't expose in GET


@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request, user: Optional[str] = Depends(optional_auth)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    template_path = "static/admin/index.html"
    with open(template_path, "r") as f:
        html = f.read()

    return html


@router.post("/", response_model=PageModel)
def create_page(page: PageModel):
    if db.get_page(page.slug):
        raise HTTPException(status_code=400, detail="Page already exists")
    db.add_page(PageData(**page.dict()))
    return page

@router.get("/list", response_model=List[PageModel])
def list_pages():
    return db.list_pages()

@router.get("/config", response_model=ConfigModel)
def get_config():
    config = load_or_create_config()
    return ConfigModel(
        system_note=config.system_note,
        ai_endpoint=config.ai_endpoint,
        base_llm=config.base_llm,
        temperature=config.temperature
        # Do not include ai_key
    )

@router.post("/config", response_model=ConfigModel)
def update_config(updated: ConfigModel):
    config = load_or_create_config()
    config.system_note = updated.system_note
    config.ai_endpoint = updated.ai_endpoint
    config.base_llm = updated.base_llm
    config.temperature = updated.temperature

    if updated.ai_key is not None:
        config.ai_key = updated.ai_key  # Save if provided

    save_config(config)
    return updated

# TODO: Change this? Please? Make the slug go... admin/site/{slug} or something

@router.get("/{slug}", response_model=PageModel)
def read_page(slug: str):
    page = db.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.put("/{slug}", response_model=PageModel)
def update_page(slug: str, page: PageModel):
    print("Received data:", page.dict())
    if not db.get_page(slug):
        raise HTTPException(status_code=404, detail="Page not found")
    db.update_page(PageData(**page.dict()))
    return page


@router.delete("/{slug}")
def delete_page(slug: str):
    if not db.get_page(slug):
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete_page(slug)
    return {"message": "Page deleted successfully"}