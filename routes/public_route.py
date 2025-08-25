from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from data.db import list_pages, get_page
from fastapi.templating import Jinja2Templates
from src.generator import generate_markdown_page
from src.config import get_theme


router = APIRouter(tags=["Public"])
template_path = f"static/public/{get_theme()}"
templates = Jinja2Templates(directory=template_path)

# Hey! Hey over here!!!

# Yes, here, this is where you make the main changes to the code!
    
# Sorry, sorry, I want to add something like... an AI Buildscript that lets you make the 'landing' and 'home' page with AI 
# But unfortunately, still under experimentation
# So yeah, go to /aina and ask her to make static site
# And just put it somewhere in static/public
# And make the route. 
# I know, a bit disappointing that you still have to make that much. I'm still working on an easier alternative aight?

@router.get("/")
async def serve_custom_page():
    path = f"{template_path}/index.html"
    return FileResponse(path)

@router.get("/blog", response_class=HTMLResponse)
async def home(request: Request):
    pages = list_pages()
    return templates.TemplateResponse("blog.html", {"request": request, "pages": pages})

# Dynamic route to serve blog type pages
@router.get("/blog/{slug}", response_class=HTMLResponse)
async def render_site(slug: str):
    page = get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)
    else:
        generated = generate_markdown_page(page.title,page.markdown)
        return HTMLResponse(content=generated, status_code=200)

# Example custom route in public_route.py
@router.get("/about")
async def serve_custom_page():
    return FileResponse(f"{template_path}/about.html")

# API ROUTES!!!

# API route to list all blog pages
@router.get("/api/blog")
async def api_list_pages():
    pages = list_pages()
    return JSONResponse(content=[
        {
            "slug": page.slug,
            "title": page.title,
            "content": page.content,
            "markdown": page.markdown,
            "html": page.html,
            "tags": page.tags,
            "thumb": page.thumb,
            "type": page.type,
            "created": page.created,
            "updated": page.updated,
            "author": page.author
        }
        for page in pages
    ])

# API route to get a single blog page by slug
@router.get("/api/blog/{slug}")
async def api_get_page(slug: str):
    page = get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    return JSONResponse(content={
        "slug": page.slug,
        "title": page.title,
        "content": page.content,
        "markdown": page.markdown,
        "html": page.html,
        "tags": page.tags,
        "thumb": page.thumb,
        "type": page.type,
        "created": page.created,
        "updated": page.updated,
        "author": page.author
    })