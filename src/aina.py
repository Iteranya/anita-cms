# file: services/aina.py

import json
import re
import asyncio
from typing import List, Optional, AsyncGenerator

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

# Import our schemas and services
from data.schemas import RouteData
from services.config import ConfigService
from services.forms import FormService
from services.pages import PageService
from src.llm import AIService

# --- Helper Classes and Functions ---

class StreamCancelledException(Exception):
    """Raised when a stream is intentionally cancelled by the client."""
    pass

class CancellableStream:
    """A token to allow for external cancellation of an async generator."""
    def __init__(self):
        self.cancelled = False
    
    def cancel(self):
        self.cancelled = True
    
    def reset(self):
        self.cancelled = False

def title_to_filename(title: str) -> str:
    """Converts a string into a URL-friendly slug."""
    filename = title.lower()
    filename = filename.replace(' ', '-')
    filename = re.sub(r'[^\w\s_-]', '', filename)
    return filename

# --- Main Service Class ---

class WebsiteBuilderService:
    def __init__(self, db: Session):
        self.db = db
        self.config_service = ConfigService(db)
        self.form_service = FormService(db)
        self.page_service = PageService(db)
        self.ai_service = AIService(db)

    def _generate_page_style_description(self, html: str) -> str:
        """Parses HTML to extract styling and structural elements for AI context."""
        if not html: return ""
        soup = BeautifulSoup(html, 'html.parser')
        components = []
        head = soup.find('head')
        if head:
            tags = head.find_all(['script', 'style', 'link'])
            for tag in tags:
                if tag.name == 'link' and tag.get('rel') == ['stylesheet']:
                    components.append(str(tag))
                elif tag.name in ['script', 'style']:
                    components.append(str(tag))
        navbar = soup.find('nav') or soup.find('header')
        if navbar: components.append(str(navbar))
        footer = soup.find('footer')
        if footer: components.append(str(footer))
        if components: return f"{' '.join(components)}\n\nMake the site based on this style."
        return ""

    def get_full_context_routes(self) -> List[RouteData]:
        """Aggregates route information from forms, pages, and config."""
        collected: List[RouteData] = []

        # 1. Get Form Routes from the FormService
        forms = self.form_service.get_all_forms(skip=0, limit=1000)
        for f in forms:
            form_slug = f.slug
            form_schema = f.schema
            
            # --- FIX 1: Use a list comprehension to get tag.name ---
            tag_names = [tag.name for tag in f.tags] if f.tags else []
            tags_info = f"Tags: {', '.join(tag_names)}" if tag_names else "No tags"

            submission_schema = {
                "id": "int (auto-assigned)",
                "form_slug": form_slug,
                "data": form_schema,
                "created": "ISO timestamp",
                "updated": "ISO timestamp",
                "author": "string | null",
                "custom": "object"
            }

            # Your original, detailed f-string for the usage note
            usage_note = f"""The REAL and WORKING route for '{f.title}'.
        {tags_info}

        📋 FORM SCHEMA:
        {json.dumps(form_schema, indent=2)}

        📦 SUBMISSION SCHEMA (server-side stored structure):
        {json.dumps(submission_schema, indent=2)}

        📋 AVAILABLE API ENDPOINTS:

        1. GET /forms/{form_slug}
        - Fetch form definition and schema
        - Returns: Form details including all field definitions

        2. POST /forms/{form_slug}/submit
        - Submit data to this form
        - Body: {{"data": {{"field_name": "value"}}, "custom": {{}}}}
        - Returns: Newly created submission with ID + timestamps

        3. GET /forms/{form_slug}/submissions
        - List all submissions for this form
        - Returns: Array following the Submission Schema

        4. GET /forms/{form_slug}/submissions/{{{{submission_id}}}}
        - Fetch a single submission
        - Returns: One item of the Submission Schema

        5. PUT /forms/{form_slug}/submissions/{{{{submission_id}}}}
        - Update an existing submission
        - Body: {{ "data": {{...}} }}
        - Returns: Updated submission

        6. DELETE /forms/{form_slug}/submissions/{{{{submission_id}}}}
        - Delete a specific submission
        - Returns: Confirmation
        """
            collected.append(
                RouteData(
                    name=form_slug,
                    type="form",
                    description=f.description,
                    schema=form_schema,
                    usage_note=usage_note
                )
            )

        # 2. Get Page Routes (Themes) from the PageService
        pages = self.page_service.get_all_pages(skip=0, limit=1000)
        
        # --- FIX 2: Check for 'theme' in the list of tag names ---
        theme_pages = [
            p for p in pages 
            if p.tags and any(tag.name == 'sys:theme' for tag in p.tags)
        ]
        
        for p in theme_pages:
            style_description = self._generate_page_style_description(p.html or "")
            
            # --- FIX 3: Get tag names for the schema dictionary ---
            page_tag_names = [tag.name for tag in p.tags] if p.tags else []
            
            collected.append(RouteData(
                name=p.slug, type="page", description=style_description,
                schema={"title": p.title, "slug": p.slug, "tags": page_tag_names},
                usage_note="Represents a CMS page layout and style theme."
            ))

        # 3. Get Config-Defined Routes from the ConfigService
        config_routes_raw = self.config_service.get_setting_value("routes", default=[])
        for route in config_routes_raw:
            collected.append(RouteData.parse_obj(route))

        return collected

    async def stream_website_generation(
        self, 
        context: str, 
        instruction: str, 
        cancellation_token: Optional[CancellableStream] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streams a generated website from the AI using the 'Aina' persona
        and provided context.
        """
        user_prompt = f"{context}\n\n{instruction}"
        messages = [
            {"role":"user", "content":user_prompt}
        ]
        
        async for chunk in self.ai_service.stream_chat(messages):
            if cancellation_token and cancellation_token.cancelled:
                raise StreamCancelledException("Stream was cancelled by user")
            yield chunk