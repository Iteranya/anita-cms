import json
from typing import List

from data.schemas import AlpineData
from services.collections import CollectionService
from services.labels import LabelService

# TODO: Abstract this somehow...

# These are generators to create the drag and drop component in Aina
# These DOES NOT run in runtime
# I repeat, THESE CODES DOES NOT RUN ON RUNTIME
# These are just component for the drag and drop backend builder

# --- Helpers ---

def _get_js_safe_slug(slug: str) -> str:
    """Replaces hyphens with underscores to ensure valid JS variable names."""
    return slug.replace('-', '_')

def _get_default_value(field_type: str) -> str:
    """Returns a JS literal for the default value based on field type."""
    if field_type == 'checkbox' or field_type == 'boolean':
        return 'false'
    if field_type == 'number':
        return 'null'
    if field_type == 'json' or field_type == 'labels':
        return '[]'
    return "''" # Default string

# --- Generators ---

def generate_collection_list_js(collection_slug: str, fields: List[dict]) -> str:
    """
    Creates the Javascript string for the List/Table view.
    """
    safe_slug = _get_js_safe_slug(collection_slug)
    component_name = f"list_{safe_slug}"

    return f"""
document.addEventListener('alpine:init', () => {{
    Alpine.data('{component_name}', () => ({{
        submissions: [],
        isLoading: false,
        page: 1,
        limit: 50,
        totalItems: 0,
        totalPages: 0,
        
        async init() {{
            await this.refresh();
        }},

        async refresh() {{
            this.isLoading = true;
            try {{
                // Expects response format: {{ items: [], totalItems: 0, totalPages: 0 }}
                const response = await this.$api.collections.listRecords('{collection_slug}', this.page, this.limit).execute();
                this.submissions = response.items || response; 
                this.totalItems = response.totalItems || 0;
                this.totalPages = response.totalPages || 0;
            }} catch(e) {{
                console.error('Failed to load submissions', e);
                if(Alpine.store('notifications')) Alpine.store('notifications').error('Error', 'Could not load data');
            }} finally {{
                this.isLoading = false;
            }}
        }},

        async deleteSubmission(id) {{
            if(!confirm('Are you sure you want to delete this submission?')) return;
            
            this.isLoading = true;
            try {{
                await this.$api.collections.deleteRecord('{collection_slug}', id).execute();
                if(Alpine.store('notifications')) Alpine.store('notifications').success('Deleted', 'Record removed.');
                await this.refresh();
            }} catch(e) {{
                console.error(e);
                if(Alpine.store('notifications')) Alpine.store('notifications').error('Error', 'Delete failed');
            }} finally {{
                this.isLoading = false;
            }}
        }},
        
        getValue(submission, fieldName) {{
            return (submission.data && submission.data[fieldName] !== undefined) 
                ? submission.data[fieldName] 
                : '';
        }},

        nextPage() {{
            if(this.page < this.totalPages) {{
                this.page++;
                this.refresh();
            }}
        }},

        prevPage() {{
            if(this.page > 1) {{
                this.page--;
                this.refresh();
            }}
        }}
    }}));
}});
"""


def generate_collection_editor_js(collection_slug: str, fields: List[dict]) -> str:
    """
    Creates the Javascript string for the Create/Update view.
    """
    safe_slug = _get_js_safe_slug(collection_slug)
    component_name = f"editor_{safe_slug}"
    
    # 1. Initialize properties with type awareness
    properties_init = []
    for f in fields:
        name = f['name']
        f_type = f.get('type', 'text')
        default_val = _get_default_value(f_type)
        properties_init.append(f"{name}: {default_val}")
    
    properties_str = ",\n        ".join(properties_init)

    # 2. Logic to map "this.field" into the payload
    payload_mapping = []
    for f in fields:
        name = f['name']
        payload_mapping.append(f"{name}: this.{name}")
    
    payload_str = ",\n                ".join(payload_mapping)

    # 3. Logic to populate "this.field" FROM existing data
    populate_logic = []
    for f in fields:
        name = f['name']
        populate_logic.append(f"if(data['{name}'] !== undefined) this.{name} = data['{name}'];")
    
    populate_str = "\n            ".join(populate_logic)

    # 4. Logic to reset fields
    reset_logic = []
    for f in fields:
        name = f['name']
        f_type = f.get('type', 'text')
        default_val = _get_default_value(f_type)
        reset_logic.append(f"this.{name} = {default_val};")
    
    reset_str = "\n            ".join(reset_logic)

    return f"""
document.addEventListener('alpine:init', () => {{
    Alpine.data('{component_name}', (initialData = null) => ({{
        // State
        submissionId: null,
        isEditing: false,
        isLoading: false,

        // --- Schema Fields ---
        {properties_str},

        init() {{
            if (initialData) {{
                this.loadData(initialData);
            }}
        }},

        loadData(data) {{
            // Unwrap data if it comes wrapped in a 'data' property (common in some CMSs)
            const flatData = data.data ? data.data : data;
            
            {populate_str}
            
            if(data.id) this.submissionId = data.id;
            this.isEditing = true;
        }},

        async save() {{
            this.isLoading = true;
            
            const submissionBody = {{
                {payload_str}
            }};

            try {{
                if (this.isEditing && this.submissionId) {{
                    // --- UPDATE ---
                    const payload = {{ data: submissionBody }};
                    await this.$api.collections.updateRecord('{collection_slug}', this.submissionId, payload).execute();
                    if(Alpine.store('notifications')) Alpine.store('notifications').success('Saved', 'Submission updated.');

                }} else {{
                    // --- CREATE ---
                    const payload = {{
                        collection_slug: '{collection_slug}',
                        data: submissionBody
                    }};
                    
                    await this.$api.collections.createRecord('{collection_slug}', payload).execute();
                    
                    if(Alpine.store('notifications')) Alpine.store('notifications').success('Success', 'Submission created.');
                    this.resetCollection();
                }}
                
                this.$dispatch('submission-saved');

            }} catch(e) {{
                console.error(e);
                if(Alpine.store('notifications')) Alpine.store('notifications').error('Error', 'Could not save submission.');
            }} finally {{
                this.isLoading = false;
            }}
        }},

        resetCollection() {{
            this.submissionId = null;
            this.isEditing = false;
            {reset_str}
        }}
    }}));
}});
"""

def generate_media_component(public_link:str, slug:str) -> str:
    # Ensure safe JS string
    safe_slug = _get_js_safe_slug(slug)
    return f"""
document.addEventListener('alpine:init', () => {{
    Alpine.data('{safe_slug}', () => ({{
        mediaUrl: '{public_link}'
    }}));
}});
"""

def generate_public_search_js(component_name: str, default_labels: List[str]) -> str:
    """
    Generates the JS for a public search component.
    """
    # Serialize labels to valid JS array string
    labels_js = json.dumps(default_labels)

    return f"""
document.addEventListener('alpine:init', () => {{
    // Add 'initialLabels' as a parameter here ----v
    Alpine.data('{component_name}', (initialLabels = {labels_js}) => ({{
        
        searchResults: [],    
        searchQuery: '',         
        defaultLabels: initialLabels, // Initialize with the passed labels
        
        isLoading: false,
        error: null,          

        async init() {{
            // This runs automatically ONCE. 
            // Since defaultLabels is now set via the constructor, this will work!
            if (this.defaultLabels.length > 0) {{
                await this.search(this.defaultLabels);
            }}
        }},

        async search(explicitLabels = null) {{
            this.isLoading = true;
            this.error = null;
            
            // 1. Start with the default labels as the base
            let labels = [...this.defaultLabels]; 

            if (Array.isArray(explicitLabels)) {{
                // If specific labels are passed (like during init), use them
                labels = explicitLabels;
            }} else {{
                // 2. If the user typed something, APPEND those labels to the defaults
                const rawInput = (this.searchQuery || '').trim();
                if (rawInput.length > 0) {{
                    const userLabels = rawInput.split(',')
                        .map(t => t.trim())
                        .filter(t => t.length > 0);
                    
                    // Merge defaults with user labels, ensuring no duplicates
                    labels = [...new Set([...labels, ...userLabels])];
                }}
            }}

            try {{
                // Now 'labels' contains both the hidden defaults (main:blog) 
                // AND the user's search terms.
                this.searchResults = await this.$api.public.search(labels).execute();
            }} catch (e){{
                console.error('Search failed:', e);
                this.error = 'Unable to fetch results.';
                this.searchResults = []; 
            }} finally {{
                this.isLoading = false;
            }}
        }},

        clear() {{
            this.searchQuery = '';
            this.searchResults = [];
            this.error = null;
        }}
    }}));
}});
"""

def generate_public_content_js(component_name: str) -> str:
    """
    Generates a generic content fetcher for the public site.
    """
    return f"""
document.addEventListener('alpine:init', () => {{
    Alpine.data('{component_name}', () => ({{
        content: null,
        isLoading: false,
        error: null,

        async loadBySlug(slug) {{
            this.isLoading = true;
            this.error = null;
            try {{
                this.content = await this.$api.public.getContent(slug).execute();
            }} catch (e) {{
                this.error = 'Content not found';
            }} finally {{
                this.isLoading = false;
            }}
        }}
    }}));
}});
"""

# --- Registry Generators ---

def generate_collection_alpine_components(collection_service: CollectionService) -> List[AlpineData]:
    collections = collection_service.get_all_collections(skip=0, limit=1000)
    alpine_registry: List[AlpineData] = []

    REQUIRED_TAGS = {"any:read", "any:create"}

    for collection in collections:
        label_names = {label.name for label in collection.labels}

        # Skip collections without any of the required labels
        if not label_names.intersection(REQUIRED_TAGS):
            continue

        schema_fields = collection.schema.get('fields', []) if collection.schema else []

        # 1. List Component
        list_js = generate_collection_list_js(collection.slug, schema_fields)
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

def generate_media_alpine_components(collection_service: CollectionService) -> List[AlpineData]:
    # Assuming 'media-data' is the internal collection slug for media
    all_media = collection_service.get_submissions_for_collection("media-data", 0, 100)
    alpine_registry: List[AlpineData] = []

    for media in all_media:
        # Check keys exist to prevent crashes
        if not media.data or 'slug' not in media.data:
            print(media)
            print(media.data)
            continue
        
            
        slug = media.data['slug']
        public_link = media.data.get('public_link', '')
        friendly_name = media.data.get('friendly_name', slug)
        description = media.data.get('description', '')
        print(slug)
        alpine_registry.append(AlpineData(
            slug=slug,
            name=f"Media: {friendly_name}",
            description=f"{description}",
            category="Media",
            data=generate_media_component(public_link, slug)
        ))

    return alpine_registry

def generate_public_alpine_components(label_service: LabelService) -> List[AlpineData]:
    """
    Generates standard public-facing components like Search, Page Loaders, etc.
    """
    alpine_registry: List[AlpineData] = []

    # 1. Public Search Component
    # This component can be dropped into any page to enable label-based search
    search_js = generate_public_search_js("public_search", default_labels=["any:read"])
    alpine_registry.append(AlpineData(
        slug="public-search",
        name="Public Search",
        description="Search content by labels or query string",
        category="Pages",
        data=search_js
    ))

    # 2. Public Content Loader
    # A generic component to fetch individual content items by slug
    # Personally I don't use it but someone else might
    content_js = generate_public_content_js("public_content")
    alpine_registry.append(AlpineData(
        slug="public-content",
        name="Public Content Loader",
        description="Fetch specific page content by slug asynchronously",
        category="Pages",
        data=content_js
    ))

    # 3. Public Page Group Loader Component
    # This is the thing you use to get like, blog pages...    
    label_group = label_service.get_main_label()
    for label in label_group:
        alpine_data = generate_public_search_js(
            f"{label.removeprefix('main:')}_component",
            default_labels=["any:read", label]
        )

        alpine_registry.append(AlpineData(
            slug=label.removeprefix("main:"),
            name=f"{label.removeprefix('main:')} List Component",
            description="Search content by labels or query string",
            category="Pages",
            data=alpine_data
        ))
    return alpine_registry