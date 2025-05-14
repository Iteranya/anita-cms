import asyncio
import json
import uuid
import re
from fastapi import APIRouter, Form, Body, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pathlib import Path
from src.asta import generate_markdown, edit_with_llm, stream_markdown

router = APIRouter(prefix="/asta", tags=["Admin"])

@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    # Path to template and scripts
    template_path = "static/asta/index.html"
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

@router.post("/edit-text")
async def edit_text(request: Request):
    try:
        task = await request.json()  # Get JSON body from the request
        edited_content = await edit_with_llm(task)  # Call your AI edit function
        return JSONResponse(content={"edited_content": edited_content})
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/generate-doc")
async def generate_doc(request: Request):
    try:
        data = await request.json()
        # Match the parameters sent from frontend
        current_markdown = data.get("current_markdown")
        prompt = data.get("prompt")
        result = await generate_markdown(context = current_markdown, instruction=prompt)
        return JSONResponse(content={"result": result})
    except Exception as e:
         return JSONResponse(content={"error": str(e)}, status_code=500)
    
from fastapi.responses import StreamingResponse

@router.post("/generate-doc-stream")
async def generate_doc_stream(request: Request):
    try:
        data = await request.json()
        current_markdown = data.get("current_markdown")
        prompt = data.get("prompt")

        async def markdown_stream():
            async for chunk in stream_markdown(context=current_markdown, instruction=prompt):
                yield chunk  # No "data:" prefix needed

        return StreamingResponse(markdown_stream(), media_type="text/plain")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
