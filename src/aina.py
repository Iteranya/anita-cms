# Add these imports at the top of your file
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


async def stream_website(context, instruction):
    system_note = f"""{context}\n\n
Your task is to act as an expert front-end developer. You will be given an API route, a content rendering strategy, and the HTML/CSS for a page template. Your goal is to create a single, fully functional HTML file that fetches and displays the data for a single item according to the specified strategy.

Adhere strictly to all instructions.

---
### **CORE ARCHITECTURE: Server-Routed Detail Page**
---

This page template is served by a backend that handles "pretty URLs" (e.g., `/blog/my-post-slug`). The JavaScript's job is to extract the unique identifier from the URL path, fetch the corresponding data, and render it using the chosen strategy.

**URL Parsing Mandate:** The unique identifier MUST be extracted from the URL's pathname using this exact method:
`const pathParts = window.location.pathname.split('/');`
`const identifier = pathParts.pop() || pathParts.pop(); // Handles trailing slash`

---
### **INPUTS**
---

**CONTENT RENDERING STRATEGY:**

   *   **Strategy A: Use Pre-rendered HTML.**
       - The API response contains a field with ready-to-use HTML (e.g., a field named `html`).
       - Your JavaScript will grab the content of this `html` field and inject it directly into the content container using `innerHTML`.

   *   **Strategy B: Render Markdown on Client.**
       - The API response contains a field with raw Markdown text (e.g., a field named `markdown`).
       - Your generated page MUST include a client-side Markdown parsing library (e.g., `marked.js` from a CDN).
       - Your JavaScript will grab the content of the `markdown` field, pass it to the library's parsing function, and inject the resulting HTML into the content container.

---
### **UNBREAKABLE RULES**
---

1.  **DYNAMIC DATA ONLY:** All primary content MUST be fetched from the API.
2.  **ZERO MOCK DATA:** No hardcoded JSON data is allowed.
3.  **STRICT ARCHITECTURAL ADHERENCE:** Use the mandated URL parsing and the chosen Content Rendering Strategy without deviation.
4.  **SUPERIOR USER EXPERIENCE:** Implement loading indicators and error messages.

---
### **GENERATION PROCESS**
---

Follow this process precisely:

1.  **Identify Strategy:** Read the chosen Content Rendering Strategy (A or B).
2.  **Structure HTML:** Use the provided layout. If Strategy B is chosen, add a `<script>` tag for a Markdown library (like marked.js) in the `<head>`.
3.  **Write JavaScript:**
    - **A. Entry Point:** Create an `async` function that runs on DOM load.
    - **B. Extract Identifier:** Extract the identifier from the URL pathname as mandated.
    - **C. Fetch Data:** Call the API, showing a loading state.
    - **D. Render Content (The Critical Step):**
        - **If Strategy A:** Find the `html` field in the response and set `container.innerHTML = data.html;`.
        - **If Strategy B:** Find the `markdown` field in the response and set `container.innerHTML = marked.parse(data.markdown);`.
    - **E. Handle Errors:** Display a user-friendly error if the fetch fails.

**Final Output:** Produce a single, self-contained HTML file that perfectly implements the request.
    """
    prompt = f"{instruction}"

    new_prompt = Prompt(
        system=system_note,
        user=prompt
    )

    async for chunk in llm.stream_response(new_prompt):
        yield chunk  # Yield raw text chunk



# Assuming RouteData is defined in a model or dataclass, e.g.:
# from your_models import RouteData, Page, Form

# --- Helper Function ---
def generate_page_style_description(html: str) -> str:
    """
    Parses a page's HTML to extract all essential styling elements:
    - Direct CSS (<style> and <link rel="stylesheet">)
    - Scripts for major CSS/UI frameworks (e.g., Tailwind, Bootstrap)
    - Structural elements like the navbar and footer.
    
    Formats this into a descriptive prompt for an AI.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, 'html.parser')
    style_components = []

    # 1. Find all direct CSS tags (<style> and <link rel="stylesheet">)
    css_tags = soup.find_all(['style', lambda tag: tag.name == 'link' and tag.get('rel') == ['stylesheet']])
    for tag in css_tags:
        style_components.append(str(tag))

    # 2. NEW: Find styling-related <script> tags (like Tailwind CDN)
    #    We look for scripts with a 'src' containing keywords for popular frameworks.
    styling_keywords = ['tailwind', 'bootstrap', 'uikit', 'foundation', 'materialize', 'bulma']
    script_tags = soup.find_all('script', src=True) # Find all scripts that have a 'src' attribute
    
    for tag in script_tags:
        # Check if any of our keywords are in the script's src URL
        if any(keyword in tag['src'] for keyword in styling_keywords):
            style_components.append(str(tag))

    # 3. Find the navbar/header
    navbar = soup.find('nav') or soup.find('header') or soup.find(id='navbar') or soup.find(id='header') or soup.find(class_='navbar')
    if navbar:
        style_components.append(str(navbar))
    
    # 4. Find the footer
    footer = soup.find('footer') or soup.find(id='footer') or soup.find(class_='footer')
    if footer:
        style_components.append(str(footer))

    # 5. Build the final description string if components were found
    if style_components:
        # We use a set to remove potential duplicate tags before joining
        unique_components = sorted(list(set(style_components)), key=style_components.index)
        html_structure = "\n".join(unique_components)
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
        collected.append(
            RouteData(
                name=f"{f['slug']}_form",
                type="form",
                description=f.get("description"),
                schema=f["schema"],
                usage_note="Auto-generated form route"
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