import asyncio
import json
import uuid
import re
from fastapi import APIRouter, Form, Body, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pathlib import Path
from src.asta import generate_html_stream, active_generations, title_to_filename, edit_with_ai

router = APIRouter(prefix="/asta", tags=["Admin"])

@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    # Path to template and scripts
    template_path = "templates/doc-builder/index.html"
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
        edited_content = await edit_with_ai(task)  # Call your AI edit function
        return JSONResponse(content={"edited_content": edited_content})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/generate-doc")
async def generate_doc(request: Request):
    data = await request.json()
    # Match the parameters sent from frontend
    current_markdown = data.get("current_markdown")
    prompt = data.get("prompt")
    prompt = current_markdown + prompt
    
    # Create a unique ID for this generation
    generation_id = str(uuid.uuid4())
    
    # Start generation in background
    task = asyncio.create_task(generate_html_stream(prompt, generation_id))
    active_generations[generation_id] = {"task": task, "chunks": []}
    
    # Return the ID immediately
    return {"id": generation_id}

@router.get("/stream/{generation_id}")
async def stream(generation_id: str):
    """Endpoint for streaming the generated content"""
    if generation_id not in active_generations:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    async def event_generator():
        # Send any chunks that already exist
        for chunk in active_generations[generation_id]["chunks"]:
            yield f"data: {json.dumps({'markdown_chunk': chunk})}\n\n"
            await asyncio.sleep(0.01)
        
        # Stream new chunks as they arrive
        last_chunk_idx = len(active_generations[generation_id]["chunks"])
        while not active_generations[generation_id]["task"].done():
            current_chunks = active_generations[generation_id]["chunks"]
            if len(current_chunks) > last_chunk_idx:
                # Send any new chunks
                for i in range(last_chunk_idx, len(current_chunks)):
                    yield f"data: {json.dumps({'markdown_chunk': current_chunks[i]})}\n\n"
                last_chunk_idx = len(current_chunks)
            await asyncio.sleep(0.1)
        
        # When done, send completion message
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")