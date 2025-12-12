# file: api/aina.py

import asyncio
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

# Import services, schemas, and dependencies from our new architecture
from data.database import get_db
from src.aina import WebsiteBuilderService, CancellableStream, StreamCancelledException
from data.schemas import RouteData

# Import the new, decoupled authentication dependencies
from src.dependencies import optional_user, get_current_user

router = APIRouter(prefix="/aina", tags=["Aina Website Builder"])

active_streams: Dict[str, CancellableStream] = {}

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

@router.post("/generate-website-stream")
async def generate_website_stream(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Starts a new AI website generation stream for the authenticated user.
    Cancels any pre-existing stream for that same user.
    """
    username = user.get("username") # 'sub' is the standard JWT claim for username/ID
    if not username:
        return JSONResponse(content={"error": "Invalid user token"}, status_code=400)

    try:
        data = await request.json()
        context = data.get("editor", "")
        instruction = data.get("prompt", "")
        
        # Cancel any existing stream FOR THIS USER
        if username in active_streams:
            active_streams[username].cancel()
            await asyncio.sleep(0.1) # Give a moment for the old stream to clean up

        # Create and store a new token for THIS USER
        token = CancellableStream()
        active_streams[username] = token
        
        service = WebsiteBuilderService(db)

        async def stream_generator():
            try:
                # Pass the user-specific token to the service
                async for chunk in service.stream_website_generation(context, instruction, token):
                    if await request.is_disconnected() or token.cancelled:
                        break
                    yield chunk
            except StreamCancelledException:
                yield "\n\n<!-- Stream stopped by user -->"
            finally:
                # Clean up the token for THIS USER
                if username in active_streams and active_streams[username] == token:
                    del active_streams[username]

        return StreamingResponse(stream_generator(), media_type="text/plain")

    except Exception as e:
        # Clean up on error
        if username and username in active_streams:
            del active_streams[username]
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.post("/stop-website-stream")
async def stop_website_stream(user: dict = Depends(get_current_user)):
    """Stops the current stream for the authenticated user."""
    username = user.get("username")
    if not username:
        return JSONResponse(content={"error": "Invalid user token"}, status_code=400)

    if username in active_streams:
        active_streams[username].cancel()
        # The stream_generator's finally block will handle deletion
        return JSONResponse(content={"message": "Stream stop signal sent."}, status_code=200)
    else:
        return JSONResponse(content={"message": "No active stream found for this user."}, status_code=200)

@router.get("/routes", response_model=List[RouteData])
async def api_get_all_routes(db: Session = Depends(get_db)):
    """
    Provides a comprehensive list of all discoverable routes 
    (forms, pages, etc.) by calling the WebsiteBuilderService.
    """
    service = WebsiteBuilderService(db)
    return service.get_full_context_routes()