# file: api/asta.py

from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

# Import services, schemas, and dependencies from our new architecture
from data.database import get_db
from services.asta import MarkdownService
from data.schemas import MarkdownEditRequest

# Import the new, decoupled authentication dependencies
from src.dependencies import optional_user, get_current_user

router = APIRouter(prefix="/asta", tags=["Asta Markdown Editor"])

@router.get("/", response_class=HTMLResponse)
async def get_asta_ui(request: Request, user: Optional[dict] = Depends(optional_user)):
    """Serves the static HTML for the Asta UI."""
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    template_path = "static/asta/index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Asta UI file (index.html) not found.")
        
    # Inject slug from query params, same as original logic
    slug = request.query_params.get("slug", "")
    html = html.replace(
        '<div id="slug-container" style="display: none;" data-slug=""></div>', 
        f'<div id="slug-container" style="display: none;" data-slug="{slug}">{slug}</div>'
    )
    return HTMLResponse(content=html)

@router.post("/edit-text")
async def edit_text(
    edit_request: MarkdownEditRequest, # Use Pydantic model for automatic validation
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Receives a markdown editing task, processes it with the AI via the
    MarkdownService, and returns the edited text.
    """
    try:
        markdown_service = MarkdownService(db)
        edited_content = await markdown_service.edit_markdown(edit_request)
        return JSONResponse(content={"edited_content": edited_content})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/generate-doc")
async def generate_doc(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a complete markdown document using the MarkdownService.
    """
    try:
        data = await request.json()
        context = data.get("current_markdown", "")
        instruction = data.get("prompt", "")
        
        markdown_service = MarkdownService(db)
        result = await markdown_service.generate_markdown(context=context, instruction=instruction)
        
        return JSONResponse(content={"result": result})
    except Exception as e:
         return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/generate-doc-stream")
async def generate_doc_stream(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streams a generated markdown document using the MarkdownService.
    """
    try:
        data = await request.json()
        context = data.get("current_markdown", "")
        instruction = data.get("prompt", "")

        markdown_service = MarkdownService(db)
        
        return StreamingResponse(
            markdown_service.stream_markdown(context=context, instruction=instruction), 
            media_type="text/plain"
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)