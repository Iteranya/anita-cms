from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from data.models import RouteData
from src.auth import optional_auth,get_current_user
from src.aina import get_routes, stream_website

router = APIRouter(prefix="/aina", tags=["Aina"])

@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request, user: Optional[str] = Depends(optional_auth)):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    # Path to template and scripts
    template_path = "static/aina/index.html"
    slug = request.query_params.get("slug", "")
    
    # Read HTML template
    with open(template_path, "r") as f:
        html = f.read()
   
    # Insert the slug value into the invisible container
    html = html.replace(
        '<div id="slug-container" style="display: none;" data-slug=""></div>', 
        f'<div id="slug-container" style="display: none;" data-slug="{slug}">{slug}</div>'
    )
    return html

@router.post("/generate-website-stream")
async def generate_website_stream(request: Request,user: dict = Depends(get_current_user)):
    try:
        data = await request.json()
        editor = data.get("editor")
        prompt = data.get("prompt")

        async def markdown_stream():
            async for chunk in stream_website(context=editor, instruction=prompt):
                yield chunk  # No "data:" prefix needed

        return StreamingResponse(markdown_stream(), media_type="text/plain")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/routes", response_model=List[RouteData])
async def api_get_all_routes():
    """
    Provides a comprehensive list of all discoverable routes 
    (forms, pages, etc.) for the frontend helper.
    """
    all_routes = get_routes()
    # The `response_model` will handle converting dataclasses to dicts
    return all_routes