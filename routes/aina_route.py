# file: api/aina.py

from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from src.alpine_generator import generate_form_alpine_components, generate_media_alpine_components, generate_public_alpine_components
from data.database import get_db
from data.schemas import AlpineData

# Import the new, decoupled authentication dependencies
from services.forms import FormService
from src.dependencies import optional_user

router = APIRouter(tags=["Aina Website Builder"])

@router.get("/aina", response_class=HTMLResponse)
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










@router.get("/routes", response_model=List[AlpineData])
async def api_get_all_routes(db: Session = Depends(get_db)):
    """
    Provides a comprehensive list of all discoverable routes 
    (forms, media wrappers, and public utilities).
    
    Includes error handling to ensure partial success if one subsystem fails.

    This is used for the dropdown menu
    """
    form_service = FormService(db)
    
    all_routes: List[AlpineData] = []
    
    # 1. Generate Components for Dynamic Forms (List & Editor views)
    try:
        form_components = generate_form_alpine_components(form_service)
        all_routes.extend(form_components)
    except Exception as e:
        print(f"Error generating form components: {e}")
        # Log the error but continue so other routes still load
    
    # 2. Generate Components for Media items
    try:
        media_components = generate_media_alpine_components(form_service)
        all_routes.extend(media_components)
    except Exception as e:
        print(f"Error generating media components: {e}")
    
    # 3. Generate Static Public Utility Components (Search, Content Loader)
    try:
        public_components = generate_public_alpine_components()
        all_routes.extend(public_components)
    except Exception as e:
        print(f"Error generating public components: {e}")

    return all_routes