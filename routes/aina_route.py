import os
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

# Data & Logic
from services.tags import TagService
from src.alpine_generator import generate_form_alpine_components, generate_media_alpine_components, generate_public_alpine_components
from data.database import get_db
from data.schemas import AlpineData
from services.forms import FormService
from src.dependencies import optional_user

router = APIRouter(tags=["Aina Website Builder"])
# TODO: Use Patch instead of Put to remove race condition in the web builder
# --- CONFIG ---
AINA_DIR = "static/aina"
ALLOWED_VIEWS = {"editor", "generator"}

# --- HELPERS ---

def render_view(file_path: str, context: dict = None):
    """
    Reads the HTML file and performs simple string replacement (templating).
    Adds anti-caching headers for HTMX.
    """
    if not os.path.exists(file_path):
        # Fallback or Error
        print(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="View template not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Simple Templating: Replace {{ key }} with value
    if context:
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}" # {{ key }}
            content = content.replace(placeholder, str(value))

    response = HTMLResponse(content)
    
    # Crucial for HTMX to know the history stack might change
    response.headers["Vary"] = "HX-Request"
    response.headers["Cache-Control"] = "no-store, max-age=0"

    return response


# --- ROUTES ---

@router.get("/aina/routes", response_model=List[AlpineData])
async def api_get_all_routes(db: Session = Depends(get_db)):
    """
    API Endpoint: Provides the list of components for the Generator.
    """
    form_service = FormService(db)
    tag_service = TagService(db)
    all_routes: List[AlpineData] = []
    
    # 1. Form Components
    try:
        all_routes.extend(generate_form_alpine_components(form_service))
    except Exception as e:
        print(f"Error generating form components: {e}")
    
    # 2. Media Components
    try:
        all_routes.extend(generate_media_alpine_components(form_service))
    except Exception as e:
        print(f"Error generating media components: {e}")
    
    # 3. Public Utils
    try:
        all_routes.extend(generate_public_alpine_components(tag_service))
    except Exception as e:
        print(f"Error generating public components: {e}")

    return all_routes


@router.get("/aina/{view_type}/{slug}", response_class=HTMLResponse)
async def aina_router(
    view_type: str, 
    slug: str, 
    request: Request, 
    user: Optional[dict] = Depends(optional_user)
):
    """
    The Main Router for the IDE.
    Handles Shell vs Partial rendering based on HTMX headers.
    """
    # 1. Auth Check
    if not user:
        return RedirectResponse(url=f"/auth/login?next=/aina/{view_type}/{slug}", status_code=302)

    # 2. Validate View Type
    if view_type not in ALLOWED_VIEWS:
        raise HTTPException(status_code=404, detail="Invalid View Type")

    # 3. Prepare Context for Templating
    context = {
        "slug": slug
    }

    # --- CASE A: HTMX Request (The Partial) ---
    # The user clicked a tab inside the shell. Return ONLY the content.
    if request.headers.get("HX-Request"):
        view_path = os.path.join(AINA_DIR, "views", f"{view_type}.html")
        return render_view(view_path, context)

    # --- CASE B: Browser Request (The Shell) ---
    # The user refreshed the page or typed the URL. Return the Shell.
    # The Shell will use the URL to highlight the correct tab, but 
    # we need to inject the slug into the shell's header/nav as well.
    shell_path = os.path.join(AINA_DIR, "index.html")
    return render_view(shell_path, context)