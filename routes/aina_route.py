import asyncio
from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)

from data.models import RouteData
from src.aina import (
    CancellableStream,
    StreamCancelledException,
    get_routes,
    stream_website,
)
from src.auth import get_current_user, optional_auth

router = APIRouter(prefix="/aina", tags=["Aina"])
current_stream_token: Optional[CancellableStream] = None


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
        f'<div id="slug-container" style="display: none;" data-slug="{slug}">{slug}</div>',
    )
    return html


@router.post("/generate-website-stream")
async def generate_website_stream(
    request: Request, user: dict = Depends(get_current_user)
):
    global current_stream_token

    try:
        data = await request.json()
        editor = data.get("editor")
        prompt = data.get("prompt")

        # Cancel any existing stream
        if current_stream_token:
            current_stream_token.cancel()
            await asyncio.sleep(0.1)  # Let it cleanup

        # Create new token
        current_stream_token = CancellableStream()
        my_token = current_stream_token  # Keep reference

        async def markdown_stream():
            global current_stream_token  # ⭐ ADD THIS LINE
            try:
                async for chunk in stream_website(
                    context=editor, instruction=prompt, cancellation_token=my_token
                ):
                    # Check if we got replaced or client disconnected
                    if await request.is_disconnected() or my_token.cancelled:
                        break
                    yield chunk
            except StreamCancelledException:
                yield "\n\n<!-- Stream stopped -->"
            finally:
                # Clear global token if we're still the current one
                if current_stream_token == my_token:
                    current_stream_token = None

        return StreamingResponse(
            markdown_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/stop-website-stream")
async def stop_website_stream(request: Request, user: dict = Depends(get_current_user)):
    """Stop the current stream"""
    global current_stream_token

    try:
        if current_stream_token:
            current_stream_token.cancel()
            return JSONResponse(content={"message": "Stream stopped"}, status_code=200)
        else:
            return JSONResponse(
                content={"message": "No active stream"}, status_code=200
            )

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
