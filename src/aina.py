# Add these imports at the top of your file
import json
from bs4 import BeautifulSoup
from typing import List 
from typing import List
from src import llm,config
from data.models import Form, Page, Prompt,RouteData
from concurrent.futures import ThreadPoolExecutor
from data.forms_db import list_forms
from data.db import list_pages
# Create a thread pool for CPU-bound tasks
executor = ThreadPoolExecutor()

def title_to_filename(title):
    # Convert to lowercase
    filename = title.lower()
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '-')
    
    # Remove special characters
    import re
    filename = re.sub(r'[^\w\s_-]', '', filename)
    
    return filename    

# I swear to god, holy shit, this is the ONLY prompt engineering that works. Forget Golden Prompt, this is it, this is the only way. I don't know why, but if you use bullshit like this:

# """{context}\n\n
# Your task is to act as an expert front-end developer. You will be given an API route, a content rendering strategy, and the HTML/CSS for a page template. Your goal is to create a single, fully functional HTML file that fetches and displays the data for a single item according to the specified strategy.

# Adhere strictly to all instructions.

# ---
# ### **CORE ARCHITECTURE: Server-Routed Detail Page**
# ---

# This page template is served by a backend that handles "pretty URLs" (e.g., `/blog/my-post-slug`). The JavaScript's job is to extract the unique identifier from the URL path, fetch the corresponding data, and render it using the chosen strategy.

# **URL Parsing Mandate:** The unique identifier MUST be extracted from the URL's pathname using this exact method:
# `const pathParts = window.location.pathname.split('/');`
# `const identifier = pathParts.pop() || pathParts.pop(); // Handles trailing slash`

# ---
# ### **INPUTS**
# ---

# **CONTENT RENDERING STRATEGY:**

#    *   **Strategy A: Use Pre-rendered HTML.**
#        - The API response contains a field with ready-to-use HTML (e.g., a field named `html`).
#        - Your JavaScript will grab the content of this `html` field and inject it directly into the content container using `innerHTML`.

#    *   **Strategy B: Render Markdown on Client.**
#        - The API response contains a field with raw Markdown text (e.g., a field named `markdown`).
#        - Your generated page MUST include a client-side Markdown parsing library (e.g., `marked.js` from a CDN).
#        - Your JavaScript will grab the content of the `markdown` field, pass it to the library's parsing function, and inject the resulting HTML into the content container.

# ---
# ### **UNBREAKABLE RULES**
# ---

# 1.  **ZERO MOCK DATA:** No hardcoded JSON data is allowed.
# 2.  **STRICT ARCHITECTURAL ADHERENCE:** Use the mandated URL parsing and the chosen Content Rendering Strategy without deviation.
# 3.  **SUPERIOR USER EXPERIENCE:** Implement loading indicators and error messages.

# ---
# ### **GENERATION PROCESS**
# ---

# Follow this process precisely:

# 1.  **Identify Strategy:** Read the chosen Content Rendering Strategy (A or B).
# 2.  **Structure HTML:** Use the provided layout. If Strategy B is chosen, add a `<script>` tag for a Markdown library (like marked.js) in the `<head>`.
# 3.  **Write JavaScript:**
#     - **A. Entry Point:** Create an `async` function that runs on DOM load.
#     - **B. Extract Identifier:** Extract the identifier from the URL pathname as mandated.
#     - **C. Fetch Data:** Call the API, showing a loading state.
#     - **D. Render Content (The Critical Step):**
#         - **If Strategy A:** Find the `html` field in the response and set `container.innerHTML = data.html;`.
#         - **If Strategy B:** Find the `markdown` field in the response and set `container.innerHTML = marked.parse(data.markdown);`.
#     - **E. Handle Errors:** Display a user-friendly error if the fetch fails.

# **Final Output:** Produce a single, self-contained HTML file that perfectly implements the request.
#     """

# It just don't work... And the AI gets confused.
# This is the only prompt engineering that I know works perfectly, FIGHT ME!!
import asyncio
from typing import Optional

class StreamCancelledException(Exception):
    """Raised when stream is intentionally cancelled"""
    pass

class CancellableStream:
    def __init__(self):
        self.cancelled = False
    
    def cancel(self):
        """Call this to stop the stream"""
        self.cancelled = True
    
    def reset(self):
        """Reset for reuse"""
        self.cancelled = False

async def stream_website(context, instruction, cancellation_token: Optional[CancellableStream] = None):
    """
    Now with emergency brake! 🛑
    
    Usage:
        token = CancellableStream()
        async for chunk in stream_website(ctx, instr, token):
            if user_said_stop:
                token.cancel()
            yield chunk
    """
    system_note = f"ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. Also, try to ellaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE \n\n <context> {context} </context>"
    prompt = f"{instruction}"

    new_prompt = Prompt(
        system=system_note,
        user=prompt
    )

    message = [
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
        {"role":"user", "content":prompt}
    ]

    async for chunk in llm.stream_message_response(new_prompt, message):
        # Check if we should stop
        if cancellation_token and cancellation_token.cancelled:
            raise StreamCancelledException("Stream was cancelled by user")
        
        yield chunk


def generate_page_style_description(html: str) -> str:
    """
    Parses a page's HTML to extract all essential styling and configuration elements
    by leveraging standard document structure. It grabs:
    
    1. Everything from the <head>: <script>, <style>, <link rel="stylesheet">.
    2. Structural landmarks from the <body>: <nav> and <footer>.
    
    Formats this into a descriptive prompt for an AI.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, 'html.parser')
    style_components = []

    # --- Part 1: Process the <head> section ---
    head_section = soup.find('head')
    if head_section:
        # Find every single script, style, and stylesheet link within the head
        tags_from_head = head_section.find_all(['script', 'style', 'link'])
        
        for tag in tags_from_head:
            # For <link> tags, make sure it's a stylesheet
            if tag.name == 'link':
                if tag.get('rel') == ['stylesheet']:
                    style_components.append(str(tag))
            else: # For <script> and <style>, add them directly
                style_components.append(str(tag))

    # --- Part 2: Process the <body> for structural elements ---
    # Find the navbar/header
    navbar = soup.find('nav') or soup.find('header') or soup.find(id='navbar') or soup.find(id='header') or soup.find(class_='navbar')
    if navbar:
        style_components.append(str(navbar))
    
    # Find the footer
    footer = soup.find('footer') or soup.find(id='footer') or soup.find(class_='footer')
    if footer:
        style_components.append(str(footer))

    # --- Part 3: Assemble the final description ---
    if style_components:
        html_structure = "\n".join(style_components)
        return f"{html_structure}\n\nMake the site based on this style."

    return ""

# --- Your Main Function (Now Modified) ---
def get_routes() -> List[RouteData]:
    print("Nyaaaa~")
    print("Mitochondrian~")

    # Load DB forms + pages
    forms = list_forms()
    pages = list_pages()

    # Load config routes (media, blog, file routes etc.)
    config_file = config.load_or_create_config()
    config_routes = config_file.routes or []

    collected: List[RouteData] = []

    # 1️⃣ Add FORM routes
    for f in forms:
        # Generate comprehensive API documentation for AI agents
        form_slug = f['slug']
        form_schema = f['schema']
        tags_info = f"Tags: {', '.join(f.get('tags', []))}" if f.get('tags') else "No tags"
        
        usage_note = f"""The REAL and WORKING route for '{f.get('title', form_slug)}'.
{tags_info}

📋 FORM SCHEMA:
{json.dumps(form_schema, indent=2)}

📋 AVAILABLE API ENDPOINTS:

1. GET /forms/{form_slug}
   - Fetch form definition and schema
   - Returns: Form details including all field definitions

2. POST /forms/{form_slug}/submit
   - Submit data to this form
   - Body: {{"data": {{"field_name": "field_value"}}, "custom": {{}}}}
   - Returns: Submission confirmation with ID and timestamp

3. GET /forms/{form_slug}/submissions
   - List all submissions for this form
   - Returns: Array of all form submissions

4. PUT /forms/{form_slug}/submissions/{{submission_id}}
   - Update an existing submission
   - Body: {{"data": {{"field_name": "field_value"}}}}

5. DELETE /forms/{form_slug}/submissions/{{submission_id}}
   - Delete a specific submission
"""
        
        collected.append(
            RouteData(
                name=f"{form_slug}_form",
                type="form",
                description=f.get("description"),
                schema=f["schema"],
                usage_note=usage_note
            )
        )

    # 2️⃣ Add PAGE routes (Now with BeautifulSoup!)
    for p in pages:
        # Generate the special description using our new helper function
        style_description = generate_page_style_description(p.html)
        
        collected.append(
            RouteData(
                name=p.slug,
                type="page",
                # Use the souped description here!
                description=style_description,
                schema={
                    "title": p.title,
                    "slug": p.slug,
                    "tags": p.tags or [],
                    "thumb": p.thumb,
                    "type": p.type,
                    "created": p.created,
                    "updated": p.updated,
                    "custom": p.custom or {}
                },
                usage_note="Represents a CMS page"
            )
        )

    # 3️⃣ Add CONFIG-DEFINED ROUTES (media, blog, etc.)
    collected.extend(config_routes)

    return collected