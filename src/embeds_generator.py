from typing import List
# Assuming these imports exist based on your environment
from data.models import Page
from data.schemas import EmbedData, PageBase
from services.forms import FormService
from services.pages import PageService 
# from services.forms import FormService # If you need to type hint the service

# --- Helpers ---

def _escape_html(text: str) -> str:
    """Basic HTML escaping for attributes."""
    if not text: 
        return ""
    return text.replace('"', '&quot;').replace("'", "&#39;")

# --- HTML Generators (Pages) ---

def generate_card_embed_html(page: PageBase, slug: str) -> str:
    """Generates a visual 'Card' embed HTML snippet."""
    safe_title = _escape_html(page.title)
    safe_desc = _escape_html(page.content or "")
    thumb_url = page.thumb if page.thumb else "https://placehold.co/600x400?text=No+Image"
    
    return f"""
<div class="embed-card" style="border:1px solid #ddd; border-radius:8px; overflow:hidden; max-width:400px; margin:1rem 0;">
    <a href="/pages/{slug}" style="text-decoration:none; color:inherit;">
        <div class="embed-thumb" style="height:200px; overflow:hidden;">
            <img src="{thumb_url}" alt="{safe_title}" style="width:100%; height:100%; object-fit:cover;">
        </div>
        <div class="embed-content" style="padding:1rem;">
            <h3 style="margin-top:0;">{safe_title}</h3>
            <p style="color:#666; font-size:0.9rem;">{safe_desc}</p>
        </div>
    </a>
</div>
"""

def generate_iframe_embed_html(page: PageBase, slug: str) -> str:
    """Generates an Iframe embed."""
    safe_title = _escape_html(page.title)
    return f"""<iframe src="/pages/{slug}" title="{safe_title}" width="100%" height="600px" frameborder="0" loading="lazy"></iframe>"""

def generate_link_embed_html(page: PageBase, slug: str) -> str:
    """Generates a simple text link."""
    safe_title = _escape_html(page.title)
    return f"""<a href="/pages/{slug}" title="{safe_title}">{safe_title}</a>"""

# --- HTML Generators (Media) ---

def generate_media_label_html(url: str, alt: str, desc: str = "") -> str:
    """Generates a standard HTML <figure> label."""
    safe_alt = _escape_html(alt)
    safe_desc = _escape_html(desc)
    caption_html = f"<figcaption>{safe_desc}</figcaption>" if desc else ""
    
    return f"""
<figure class="media-embed">
    <img src="{url}" alt="{safe_alt}" style="max-width:100%; height:auto;">
    {caption_html}
</figure>
"""

def generate_media_markdown(url: str, alt: str) -> str:
    """Generates a Markdown image string."""
    # Note: Markdown doesn't handle quotes in alt text gracefully without escaping, 
    # but standard practice is usually just square brackets.
    return f"![{alt}]({url})"

# --- Registry Generators ---

def generate_page_embeds(page_service:PageService) -> List[EmbedData]:
    """
    Generates embeds for Pages.
    Expects 'pages' to be a list of DB objects with .slug and .data attributes.
    """
    embed_registry: List[EmbedData] = []
    pages:List[Page] = page_service.get_pages_by_label("any:read") # TODO: Make this filter only markdown-type page
    for item in pages:
        slug = item.slug
        
        if not slug: 
            continue

        # 1. Visual Card
        embed_registry.append(EmbedData(
            slug=f"page-card-{slug}",
            name=f"Page Card: {item.title}",
            description=f"Visual link card for {item.title}",
            category="Pages",
            data=generate_card_embed_html(item, slug)
        ))

        # 2. Iframe
        embed_registry.append(EmbedData(
            slug=f"page-frame-{slug}",
            name=f"Page Frame: {item.title}",
            description="Embed full page via Iframe",
            category="Pages",
            data=generate_iframe_embed_html(item, slug)
        ))
        
        # 3. Simple Link
        embed_registry.append(EmbedData(
            slug=f"page-link-{slug}",
            name=f"Page Link: {item.title}",
            description="Simple text hyperlink",
            category="Pages",
            data=generate_link_embed_html(item, slug)
        ))

    return embed_registry

def generate_media_embeds(form_service:FormService) -> List[EmbedData]:
    """
    Generates embeds for Media items (Images, etc).
    Expects 'media_items' to be a list of DB objects from the 'media-data' form.
    """
    embed_registry: List[EmbedData] = []
    media_items = form_service.get_submissions_for_form("media-data")
    for media in media_items:
        # Safety checks
        if not media.data or 'slug' not in media.data:
            continue
            
        slug = media.data['slug']
        public_link = media.data.get('public_link', '')
        friendly_name = media.data.get('friendly_name', slug)
        description = media.data.get('description', '')
        
        if not public_link:
            continue

        # 1. HTML Image Label (with optional caption)
        embed_registry.append(EmbedData(
            slug=f"media-html-{slug}",
            name=f"Image (HTML): {friendly_name}",
            description=f"Standard HTML <img> label for {friendly_name}",
            category="Media",
            data=generate_media_label_html(public_link, friendly_name, description)
        ))

        # 2. Markdown Image Syntax (Great for inserting into the markdown post directly)
        embed_registry.append(EmbedData(
            slug=f"media-md-{slug}",
            name=f"Image (Markdown): {friendly_name}",
            description=f"Markdown syntax ![alt](url) for {friendly_name}",
            category="Media",
            data=generate_media_markdown(public_link, friendly_name)
        ))

        # 3. Raw URL (Just the link)
        embed_registry.append(EmbedData(
            slug=f"media-url-{slug}",
            name=f"Raw URL: {friendly_name}",
            description="The direct public link to the file",
            category="Media",
            data=public_link
        ))

    return embed_registry