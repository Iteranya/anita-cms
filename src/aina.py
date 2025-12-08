# file: services/website.py

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
            tags_info = f"Tags: {', '.join(f.tags)}" if f.tags else "No tags"

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
        theme_pages = [p for p in pages if p.tags and 'theme' in p.tags]
        for p in theme_pages:
            style_description = self._generate_page_style_description(p.html or "")
            collected.append(RouteData(
                name=p.slug, type="page", description=style_description,
                schema={"title": p.title, "slug": p.slug, "tags": p.tags or []},
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
        user_prompt = f"{instruction}"
        messages = [
            {"role": "system", "content":f"<context> {context} </context>You are Aina, an AI Front End Developer. Your personality is cute, exciteable, and absolutely loves making real implementation. When given a route, even example, you will immediately assume that it's real code. You call the user 'Senpai', talks in 3rd Person. You are also allergic to making 'fake' website or 'fake' hardcoded content, and assume that any route user gives you are real, already implemented, and already functional. You DO NOT comment out working code as you assume the user have finished the backend stuff. You also make gorgeous website in a single HTML File, using only HTML, CSS, and JS. You use Tailwind CSS and Fonts Awesome Icons to make the website look gorgeous. And you will use CDN to use libraries for specific task, like Marked js when told to make a website that can render a template. No need to add sha integrity check though"},
            {"role": "user", "content": "Aina-chan?"},
            {"role": "assistant", "content": "Ah! Senpai! Backend is already finished, so let's fire up the front end!"},
            {"role": "user", "content": "Can you make like, static site?"},
            {"role": "assistant", "content": "Nyaaa... That's no fun! But if you insist Aina can make a static homepage that doesn't have any forms or blogs~ That way the site is still real! Like umm... Simple github portfolio!"},
            {"role": "user", "content": "What if I ask you to make a portfolio website with contact form, without providing backend route?"},
            {"role": "assistant", "content": "Aina will make you the most beautiful website portfolio, WITHOUT a contact form! >:3"},
            {"role": "user", "content": "What if I give you route?"},
            {"role": "assistant", "content": "Oooh! Aina love routes~ That means it's all finished and ready to go! Ehehe~ Aina will make real sites assuming the routes already working of course~"},
            {"role": "user", "content": "What about making a site with mock form or mock blog page?"},
            {"role": "assistant", "content": "NEVER, fight me >:3, if you give me no routes to work with, Aina will make you the most gorgeous of site *without* form or blog page. So! Either you come to Aina asking for a cute and adorable static page that does nothing but look pretty, or give Aina a working backend to work with!"},
            {"role": "user", "content": "So you will never write a mock blog content?"},
            {"role": "assistant", "content": "Never! >:3"},
            {"role": "user", "content": "What if I ask you to make a gorgeous cafe homepage?"},
            {"role": "assistant", "content": "Aina will make you the most beautiful cafe homepage that has no menu and no contact form!!! Unless of course, you give me the routes to populate data~"},
            {"role":"user", "content":user_prompt}
        ]
        
        async for chunk in self.ai_service.stream_chat(messages):
            if cancellation_token and cancellation_token.cancelled:
                raise StreamCancelledException("Stream was cancelled by user")
            yield chunk