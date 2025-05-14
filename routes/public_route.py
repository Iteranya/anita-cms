from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from data.db import list_pages, get_page
from fastapi.templating import Jinja2Templates
from src.generator import generate_markdown_page
router = APIRouter(tags=["Public"])
templates = Jinja2Templates(directory="static/public")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    pages = list_pages()
    return templates.TemplateResponse("index.html", {"request": request, "pages": pages})

# Dynamic route to serve saved pages as raw HTML
@router.get("/site/{slug}", response_class=HTMLResponse)
async def render_site(slug: str):
    page = get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if page.html != None and page.html != "":
        return HTMLResponse(content=page.html, status_code=200)
    else:
        generated = generate_markdown_page(page.title,page.markdown)
        return HTMLResponse(content=generated, status_code=200)
