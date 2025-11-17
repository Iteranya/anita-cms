from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from data.db import list_pages, get_page
from fastapi.templating import Jinja2Templates
from src.generator import generate_markdown_page
from src.config import get_theme


router = APIRouter(tags=["Public"])
template_path = f"static/public/{get_theme()}"
templates = Jinja2Templates(directory=template_path)

@router.get("/", response_class=HTMLResponse)
async def serve_custom_page(request: Request):
    # Get all pages
    pages = list_pages()

    # Try to find the first page with 'home' tag
    home_page = next((page for page in pages if page.tags and 'home' in page.tags), None)

    if home_page:
        # If page is HTML, serve it directly
        if home_page.type == 'html':
            return HTMLResponse(content=home_page.html, status_code=200)
        else:
            # Otherwise, generate HTML from Markdown
            generated = generate_markdown_page(home_page.title, home_page.markdown)
            return HTMLResponse(content=generated, status_code=200)
    
    # Fallback to static index.html if no 'home' page found
    path = f"{template_path}/index.html"
    return FileResponse(path)


@router.get("/blog/", response_class=HTMLResponse)
async def home(request: Request):
    pages = list_pages()
    pages = list_pages()
    blog_pages = [page for page in pages if page.tags and 'blog' in page.tags]
    blog_home = next((page for page in pages if page.tags and 'blog-home' in page.tags), None)

    if blog_home:
        if blog_home.type == 'html':
            return HTMLResponse(content=blog_home.html, status_code=200)

    # Fallback to blog.html template with list of pages
    return templates.TemplateResponse("blog.html", {"request": request, "pages": blog_pages})

# Dynamic route to serve blog type pages
@router.get("/blog/{slug}", response_class=HTMLResponse)
async def render_site(slug: str):
    page = get_page(slug)
    if not page or not (page.tags and 'blog' in page.tags):
        raise HTTPException(status_code=404, detail="Main page not found")
    pages = list_pages()
    template = next((page for page in pages if page.tags and 'blog-template' in page.tags), None)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)
    elif template:
        generated = generate_markdown_page(page.title,page.markdown,template.html)
        return HTMLResponse(content=generated, status_code=200)
    else:
        generated = generate_markdown_page(page.title,page.markdown)
        return HTMLResponse(content=generated, status_code=200)

# Dynamic route to serve 'main' pages
@router.get("/{slug}/", response_class=HTMLResponse)
async def serve_main_page(slug: str):
    page = get_page(slug)

    # Check if page exists and has the 'main' tag
    if not page or not (page.tags and 'main' in page.tags):
        raise HTTPException(status_code=404, detail="Main page not found")

    # If it's pure HTML, return as is
    if page.type == 'html':
        return HTMLResponse(content=page.html, status_code=200)

    # Otherwise, generate HTML from Markdown
    generated = generate_markdown_page(page.title, page.markdown)
    return HTMLResponse(content=generated, status_code=200)

# API ROUTES!!!

# API route to list all blog pages
@router.get("/api/blog")
async def api_list_pages():
    pages = list_pages()
    
    blog_pages = [
        page for page in pages
        if page.tags and "blog" in page.tags
    ]
    
    return JSONResponse(content=[
        {
            "slug": page.slug,
            "title": page.title,
            "content": page.content,
            "tags": page.tags or [],
            "thumb": page.thumb,
            "type": page.type,
            "created": page.created,
            "updated": page.updated,
            "author": page.author
        }
        for page in blog_pages
    ])


# API route to get a single blog page by slug
@router.get("/api/blog/{slug}")
async def api_get_page(slug: str):
    page = get_page(slug)
    if not "blog" in page.tags:
        raise HTTPException(status_code=404, detail="Page not found")
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    return JSONResponse(content={
        "slug": page.slug,
        "title": page.title,
        "content": page.content,
        "markdown": page.markdown,
        "html": page.html,
        "tags": page.tags or [],
        "thumb": page.thumb,
        "type": page.type,
        "created": page.created,
        "updated": page.updated,
        "author": page.author
    })