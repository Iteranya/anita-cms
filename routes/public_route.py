from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from data.db import list_pages, get_page
from fastapi.templating import Jinja2Templates
from src.generator import generate_markdown_page


router = APIRouter(tags=["Public"])
templates = Jinja2Templates(directory="static/public")

# Hey! Hey over here!!!

# Yes, here, this is where you make the main changes to the code!
    
# Sorry, sorry, I want to add something like... an AI Buildscript that lets you make the 'landing' and 'home' page with AI 
# But unfortunately, still under experimentation
# So yeah, go to /aina and ask her to make static site
# And just put it somewhere in static/public
# And make the route. 
# I know, a bit disappointing that you still have to make that much. I'm still working on an easier alternative aight?

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    pages = list_pages()
    return templates.TemplateResponse("index.html", {"request": request, "pages": pages})

# Dynamic route to serve blog type pages
@router.get("/site/{slug}", response_class=HTMLResponse)
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
    return FileResponse("static/public/about.html")