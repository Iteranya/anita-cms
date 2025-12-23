# file: api/aina.py

from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from data.database import get_db
from services.aina import WebsiteBuilderService
from data.schemas import RouteData

# Import the new, decoupled authentication dependencies
from src.dependencies import optional_user

router = APIRouter(prefix="/aina", tags=["Aina Website Builder"])

@router.get("/", response_class=HTMLResponse)
async def get_aina_ui(request: Request, user: Optional[dict] = Depends(optional_user)):
    """Serves the static HTML for the Aina UI."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    template_path = "static/aina/index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Aina UI file (index.html) not found.")
        
    # Inject slug from query params, same as original logic
    slug = request.query_params.get("slug", "")
    html = html.replace(
        '<div id="slug-container" style="display: none;" data-slug=""></div>', 
        f'<div id="slug-container" style="display: none;" data-slug="{slug}">{slug}</div>'
    )
    return HTMLResponse(content=html)

@router.get("/routes", response_model=List[RouteData])
async def api_get_all_routes(db: Session = Depends(get_db)):
    """
    Provides a comprehensive list of all discoverable routes 
    (forms, pages, etc.) by calling the WebsiteBuilderService.
    """
    service = WebsiteBuilderService(db)
    return service.get_full_context_routes()

