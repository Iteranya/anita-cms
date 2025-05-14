from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from src.aina import stream_website

router = APIRouter(prefix="/aina", tags=["Aina"])

@router.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
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
async def generate_website_stream(request: Request):
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
