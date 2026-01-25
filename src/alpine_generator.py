import os
from typing import List
from jinja2 import Environment, FileSystemLoader

from data.schemas import AlpineData
from services.collections import CollectionService
from services.labels import LabelService

# --- Configuration ---

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), './templates')
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# --- Helpers ---

def _get_js_safe_slug(slug: str) -> str:
    """Replaces hyphens with underscores to ensure valid JS variable names."""
    return slug.replace('-', '_')

def _get_default_value(field_type: str) -> str:
    """Returns a JS literal for the default value based on field type."""
    if field_type in ('checkbox', 'boolean'):
        return 'false'
    if field_type == 'number':
        return 'null'
    if field_type in ('json', 'labels','object'):
        return '[]'
    return "''" # Default string

# --- Generators ---

def generate_collection_list_js(collection_slug: str) -> str:
    """Creates the Javascript string for the List/Table view."""
    safe_slug = _get_js_safe_slug(collection_slug)
    template = jinja_env.get_template('collection_list.js.j2')
    
    return template.render(
        component_name=f"list_{safe_slug}",
        collection_slug=collection_slug
    )

def generate_collection_editor_js(collection_slug: str, fields: List[dict]) -> str:
    """Creates the Javascript string for the Create/Update view."""
    safe_slug = _get_js_safe_slug(collection_slug)
    template = jinja_env.get_template('collection_editor.js.j2')

    # Pre-process fields to include default values for Jinja
    processed_fields = []
    for f in fields:
        processed_fields.append({
            'name': f['name'],
            'default_value': _get_default_value(f.get('type', 'text')),
            'type': f.get('type', 'text')
        })

    return template.render(
        component_name=f"editor_{safe_slug}",
        collection_slug=collection_slug,
        fields=processed_fields
    )

def generate_media_component(public_link: str, slug: str) -> str:
    safe_slug = _get_js_safe_slug(slug)
    template = jinja_env.get_template('media.js.j2')
    
    return template.render(
        safe_slug=safe_slug,
        public_link=public_link
    )

def generate_public_search_js(component_name: str, default_labels: List[str], base_path: str = "") -> str:
    """Generates the JS for a public search component."""
    template = jinja_env.get_template('public_search.js.j2')

    page_structure = {
        "slug": "",
        "title": "",
        "content": None,
        "labels": [],
        "tags": [],
        "thumb": None,
        "type": "markdown",
        "author": None,
        "custom": {},
        "created": "",
        "updated": ""
    }

    return template.render(
        component_name=component_name,
        default_labels=default_labels,
        base_path=base_path,
        result_schema=page_structure
    )

def generate_public_content_js(component_name: str) -> str:
    """Generates a generic content fetcher for the public site."""
    template = jinja_env.get_template('public_content.js.j2')
    
    return template.render(
        component_name=component_name
    )

def generate_markdown_js() -> str:
    """Reads the raw content of the markdown template, bypassing Jinja."""
    file_path = os.path.join(TEMPLATE_DIR, 'markdown.js.j2')
    
    # Open the file and read it as a plain string
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
    
def upload_media_js() -> str:
    """Reads the raw content of the markdown template, bypassing Jinja."""
    file_path = os.path.join(TEMPLATE_DIR, 'media_upload.js.j2')
    
    # Open the file and read it as a plain string
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
    
def list_media_js() -> str:
    """Reads the raw content of the markdown template, bypassing Jinja."""
    file_path = os.path.join(TEMPLATE_DIR, 'media_list.js.j2')
    
    # Open the file and read it as a plain string
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Registry Generators ---

def generate_collection_alpine_components(collection_service: CollectionService) -> List[AlpineData]:
    collections = collection_service.get_all_collections(skip=0, limit=1000)
    alpine_registry: List[AlpineData] = []

    REQUIRED_TAGS = {"any:read", "any:create"}

    for collection in collections:
        label_names = {label.name for label in collection.labels}

        if not label_names.intersection(REQUIRED_TAGS):
            continue

        schema_fields = collection.schema.get('fields', []) if collection.schema else []

        # 1. List Component
        list_js = generate_collection_list_js(collection.slug)
        alpine_registry.append(AlpineData(
            slug=f"list-{collection.slug}",
            name=f"List: {collection.title}",
            description=f"Displays submissions for {collection.title}",
            category="Collections",
            data=list_js
        ))

        # 2. Editor Component
        editor_js = generate_collection_editor_js(collection.slug, schema_fields)
        alpine_registry.append(AlpineData(
            slug=f"editor-{collection.slug}",
            name=f"Editor: {collection.title}",
            description=f"Create or Edit submissions for {collection.title}",
            category="Collections",
            data=editor_js
        ))
    
    return alpine_registry

def generate_media_alpine_components(collection_service: CollectionService) -> List[AlpineData]:
    # Assuming 'media-data' is the internal collection slug for media
    all_media = collection_service.get_submissions_for_collection("media-data", 0, 100)
    alpine_registry: List[AlpineData] = []

    for media in all_media:
        if not media.data or 'slug' not in media.data:
            print(f"Skipping invalid media: {media.id}")
            continue
            
        slug = media.data['slug']
        public_link = media.data.get('public_link', '')
        friendly_name = media.data.get('friendly_name', slug)
        description = media.data.get('description', '')
        
        alpine_registry.append(AlpineData(
            slug=slug,
            name=f"Media: {friendly_name}",
            description=f"{description}",
            category="Media",
            data=generate_media_component(public_link, slug)
        ))

    return alpine_registry

def generate_public_alpine_components(label_service: LabelService) -> List[AlpineData]:
    alpine_registry: List[AlpineData] = []

    #0. Create the Relational Code
    alpine_registry.append(AlpineData(
        slug="relational-code",
        name="Relational Code",
        description="A Glue Code that combines x-data together",
        category="Utility",
        data="""document.addEventListener('alpine:init', () => {
    
    // --- 1. Universal Data Store (The Bridge) ---
    Alpine.store('data_bridge', {
        cache: {}, 

        async get(collectionName, api) {
            if (this.cache[collectionName]) return this.cache[collectionName];
            try {
                const response = await api.collections.listRecords(collectionName, 0, 500).execute();
                this.cache[collectionName] = response.items || response;
                return this.cache[collectionName];
            } catch (e) {
                console.error(`Failed to load relational data for ${collectionName}`, e);
                return [];
            }
        }
    });

    // --- 2. Universal Relational Picker Component ---
    Alpine.data('relation_picker', (foreignCollectionName) => ({
        items: [],
        selected: [],
        isLoading: true,

        async init() {
            // Fetch all foreign items
            this.items = await Alpine.store('data_bridge').get(foreignCollectionName, this.$api);
            this.isLoading = false;

            // REMOVED: The code block that tried to access 'this.$parent.menu_slugs'
            // We now rely entirely on x-effect in the HTML to handle the sync.

            // Emit changes back to parent
            this.$watch('selected', (newSelection) => {
                // Prevent infinite loops by checking if the value actually differs
                // (Though Alpine usually handles basic primitive array loops okay)
                this.$dispatch('relation-changed', { 
                    collection: foreignCollectionName, 
                    values: newSelection 
                });
            });
        }
    }));
});"""
    ))

    # 1. Public Search Component
    search_js = generate_public_search_js("public_search", default_labels=["any:read"])
    alpine_registry.append(AlpineData(
        slug="public-search",
        name="Public Search",
        description="Search content by labels or query string",
        category="Pages",
        data=search_js
    ))

    # 2. Public Content Loader
    content_js = generate_public_content_js("public_content")
    alpine_registry.append(AlpineData(
        slug="public-content",
        name="Public Content Loader",
        description="Fetch specific page content by slug asynchronously",
        category="Pages",
        data=content_js
    ))

    # 3. Public Page Group Loader Components
    label_group = label_service.get_main_label()
    for label in label_group:
        base_name = label.removeprefix("main:")
        component_name = f"{base_name}_component"
        
        alpine_data = generate_public_search_js(
            component_name=component_name,
            default_labels=["any:read", label],
            base_path=base_name
        )

        alpine_registry.append(AlpineData(
            slug=base_name,
            name=f"{base_name} List Component",
            description="Search content by labels or query string",
            category="Pages",
            data=alpine_data
        ))
    return alpine_registry

def generate_markdown_renderer_js() -> List[AlpineData]:
    """Generates the JS for the Markdown renderer component."""
    
    # Get the raw string from the helper function above
    raw_content = generate_markdown_js()
    
    return [AlpineData(
        slug="markdown_renderer",
        name="Markdown Renderer",
        description="This component lets this page render markdown content",
        category="Utility",
        data=raw_content
    )]

def generate_media_upload_js() -> List[AlpineData]:
    """Generates the JS for the Markdown renderer component."""
    
    # Get the raw string from the helper function above
    raw_content = upload_media_js()
    
    return [AlpineData(
        slug="media_upload",
        name="Media Upload",
        description="This component lets this page upload media",
        category="Utility",
        data=raw_content
    )]

def generate_media_list() -> List[AlpineData]:
    """Generates the JS for the Markdown renderer component."""
    
    # Get the raw string from the helper function above
    raw_content = list_media_js()
    
    return [AlpineData(
        slug="media_list",
        name="Media List",
        description="This component lets this page list ALL media",
        category="Utility",
        data=raw_content
    )]