# file: api/asta.py

import os
import re  # <--- Import the regex module
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from data.database import get_db
from src.embeds_generator import generate_media_embeds, generate_page_embeds
from data.schemas import EmbedData
from services.collections import CollectionService
from services.pages import PageService
from src.dependencies import get_current_user

router = APIRouter(tags=["Asta Markdown Editor"])

# --- CONFIG ---
ASTA_INDEX_PATH = "static/asta/index.html"

# --- HELPER ---
def render_template(file_path: str, context: dict = None):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Editor template not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if context:
        for key, value in context.items():
            # --- THIS IS THE CORRECTED PART ---
            # Create a regex pattern to find "{{ key }}", allowing for optional spaces
            # For key="slug", this becomes: r"{{\s*slug\s*}}"
            # \s* matches zero or more whitespace characters
            pattern = re.compile(r"{{\s*" + re.escape(key) + r"\s*}}")
            
            # Use re.sub() for robust replacement
            content = pattern.sub(str(value), content)
            # --- END OF CORRECTION ---

    return HTMLResponse(content)

# --- ROUTES ---

@router.get("/asta/routes", response_model=List[EmbedData], )
async def api_get_all_routes(db: Session = Depends(get_db), user: Optional[dict] = Depends(get_current_user)):
    """API Endpoint: Provides the list of components for the Generator."""
    page_service = PageService(db)
    collection_service = CollectionService(db)
    all_routes: List[EmbedData] = []
    
    try:
        all_routes.extend(generate_page_embeds(page_service))
        all_routes.extend(generate_media_embeds(collection_service))
    except Exception as e:
        print(f"Error generating embeds: {e}")

    return all_routes


@router.get("/asta/editor/{slug}", response_class=HTMLResponse)
async def asta_editor_view(
    slug: str, 
    request: Request, 
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Serves the Single Page Application for the Editor.
    """
    if not user:
        return RedirectResponse(url=f"/auth/login?next=/asta/editor/{slug}", status_code=302)

    # This will now correctly inject the slug
    return render_template(ASTA_INDEX_PATH, {"slug": slug})