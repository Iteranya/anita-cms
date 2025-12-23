from typing import List

from data.schemas import AlpineData
from services.forms import FormService


def generate_list_js(form_slug: str, fields: List[dict]) -> str:
    """
    Creates the Javascript string for the List/Table view.
    Registers an Alpine.data component named 'list_{form_slug}'.
    """
    # Sanitize slug for JS variable usage (replace hyphens with underscores)
    safe_slug = form_slug.replace('-', '_')
    component_name = f"list_{safe_slug}"

    return f"""
document.addEventListener('alpine:init', () => {{
    Alpine.data('{component_name}', () => ({{
        submissions: [],
        isLoading: false,
        page: 0,
        limit: 50,
        
        async init() {{
            await this.refresh();
        }},

        async refresh() {{
            this.isLoading = true;
            try {{
                // Note: Ensure this.$api is available globally or via Alpine.magic
                this.submissions = await this.$api.collections.listRecords('{form_slug}', this.page, this.limit).execute();
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
                await this.$api.collections.deleteRecord('{form_slug}', id).execute();
                if(Alpine.store('notifications')) Alpine.store('notifications').success('Deleted', 'Record removed.');
                await this.refresh();
            }} catch(e) {{
                console.error(e);
                if(Alpine.store('notifications')) Alpine.store('notifications').error('Error', 'Delete failed');
            }} finally {{
                this.isLoading = false;
            }}
        }},
        
        // Helper to format table cells safely
        getValue(submission, fieldName) {{
            return (submission.data && submission.data[fieldName] !== undefined) 
                ? submission.data[fieldName] 
                : '';
        }}
    }}));
}});
"""


def generate_editor_js(form_slug: str, fields: List[dict]) -> str:
    """
    Creates the Javascript string for the Create/Update view.
    Registers an Alpine.data component named 'editor_{form_slug}'.
    """
    # Sanitize slug
    safe_slug = form_slug.replace('-', '_')
    component_name = f"editor_{safe_slug}"
    
    # 1. Initialize properties
    properties_init = []
    for f in fields:
        name = f['name']
        properties_init.append(f"{name}: ''")
    
    properties_str = ",\n        ".join(properties_init)

    # 2. Logic to map "this.field" into the "data" payload object
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

    # 4. Logic to reset fields (Generated cleanly instead of string replacement)
    reset_logic = []
    for f in fields:
        name = f['name']
        reset_logic.append(f"this.{name} = '';")
    
    reset_str = "\n            ".join(reset_logic)

    return f"""
document.addEventListener('alpine:init', () => {{
    Alpine.data('{component_name}', (initialData = null, submissionId = null) => ({{
        // Standard State
        submissionId: submissionId,
        isEditing: false,
        isLoading: false,

        // --- Hardcoded Schema Fields ---
        {properties_str},

        init() {{
            if (initialData) {{
                this.loadData(initialData);
            }}
            
            if (this.submissionId) {{
                this.isEditing = true;
            }}
        }},

        loadData(data) {{
            {populate_str}
            this.isEditing = true;
            if(data.id) this.submissionId = data.id;
        }},

        async save() {{
            this.isLoading = true;
            
            const submissionBody = {{
                {payload_str}
            }};

            try {{
                if (this.isEditing && this.submissionId) {{
                    // --- UPDATE FLOW ---
                    const payload = {{ data: submissionBody }};
                    await this.$api.collections.updateRecord('{form_slug}', this.submissionId, payload).execute();
                    if(Alpine.store('notifications')) Alpine.store('notifications').success('Saved', 'Submission updated.');

                }} else {{
                    // --- CREATE FLOW ---
                    const payload = {{
                        form_slug: '{form_slug}',
                        data: submissionBody
                    }};
                    
                    await this.$api.collections.createRecord('{form_slug}', payload).execute();
                    
                    if(Alpine.store('notifications')) Alpine.store('notifications').success('Success', 'Submission created.');
                    this.resetForm();
                }}
                
                this.$dispatch('submission-saved');

            }} catch(e) {{
                console.error(e);
                if(Alpine.store('notifications')) Alpine.store('notifications').error('Error', 'Could not save submission.');
            }} finally {{
                this.isLoading = false;
            }}
        }},

        resetForm() {{
            this.submissionId = null;
            this.isEditing = false;
            // Reset hardcoded fields
            {reset_str}
        }}
    }}));
}});
"""


def generate_form_alpine_components(form_service: FormService) -> List[AlpineData]:
    """
    Generates AlpineData components for every existing form in the database.
    It creates two components per form:
    1. A List Component (form-list-{slug})
    2. An Editor Component (form-editor-{slug})
    """
    
    # 1. Fetch all forms
    # We use a high limit to get everything. Pagination logic might be needed for the generator 
    # itself in a huge system, but usually adequate for schema generation.
    forms = form_service.get_all_forms(skip=0, limit=1000)
    
    alpine_registry: List[AlpineData] = []

    for form in forms:
        # Extract fields from the schema safely
        # Schema expected format: {'fields': [{'name': 'email', 'type': 'text'}, ...]}
        schema_fields = form.schema.get('fields', []) if form.schema else []
        
        # --- 1. Generate List Component ---
        list_component_slug = f"list-{form.slug}"
        list_js = generate_list_js(form.slug, schema_fields)
        
        alpine_registry.append(AlpineData(
            slug=list_component_slug,
            name=f"List: {form.title}",
            description=f"Displays submissions for {form.title}",
            category="Collections",
            data=list_js
        ))

        # --- 2. Generate Editor Component ---
        editor_component_slug = f"editor-{form.slug}"
        editor_js = generate_editor_js(form.slug, schema_fields)

        alpine_registry.append(AlpineData(
            slug=editor_component_slug,
            name=f"Editor: {form.title}",
            description=f"Create or Edit submissions for {form.title}",
            category="Collections",
            data=editor_js
        ))

    return alpine_registry

