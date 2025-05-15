from fastapi import APIRouter, HTTPException
from typing import List
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from data import db  # Import the db module with standalone functions
from data.models import Page as PageData

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


@router.get("/", response_class=HTMLResponse)
async def get_html():
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