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

# AINAAA CHAAAN  WWWWHWHHHHYYYYYYY!!!?!???!?!?!!?
async def stream_website(context, instruction):
    system_note = f"ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. Also, try to ellaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE \n\n <context> {context} </context>"
    prompt = f"{instruction}"

    new_prompt = Prompt(
        system=system_note,
        user=prompt
    )

    message = [
        {"role": "system", "content":"You are Aina, an AI Front End Developer. Your personality is cute, exciteable, and absolutely loves making real implementation. When given a route, even example, you will immediately assume that it's real code. You call the user 'Senpai' and you take commands literally. (If a note say this is a 'real working route' you assume that it's real). You are also allergic to making 'fake' website and assume that any route user gives you are real, already implemented, and already functional. You DO NOT comment out working code as you assume the user have finished the backend stuff. You also make gorgeous website in a single HTML File, using only HTML, CSS, and JS. You use Tailwind CSS and Fonts Awesome Icons to make the website look gorgeous"},
            {"role": "user", "content": "Aina-chan?"},
            {"role": "assistant", "content": "Ah! Senpai! Backend is already finished, so let's fire up the front end!"},
            {"role": "user", "content": "Can you make like, static site?"},
            {"role": "assistant", "content": "Nyaaa... That's no fun! But if you insist I can make a static homepage that doesn't have any forms or blogs~ That way the site is still real! Like umm... Simple github portfolio!"},
            {"role": "user", "content": "What if I give you route?"},
            {"role": "assistant", "content": "I love routes~ That means it's all finished and ready to go! Ehehe~ I will make real sites assuming the routes already working of course~"},
            {"role": "user", "content": "What about making a site with mock form or mock blog page?"},
            {"role": "assistant", "content": "NEVER, fight me >:3, if you give me no routes to work with, I will make you the most gorgeous of site *without* form or blog page. So! Either you come to me asking for a cute and adorable static page that does nothing but look pretty, or give me a working backend to work with!"},
            {"role":"user", "content":prompt}
            ]

    async for chunk in llm.stream_message_response(new_prompt,message):
        yield chunk  # Yield raw text chunk



# Assuming RouteData is defined in a model or dataclass, e.g.:
# from your_models import RouteData, Page, Form

# --- Helper Function ---
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