// ===================================================================
//  HIKARIN JS - Universal No-Code Bridge
// ===================================================================

class HikarinApiError extends Error {
    constructor(message, status, detail) {
        super(message);
        this.name = 'HikarinApiError';
        this.status = status;
        this.detail = detail;
    }
}

class ApiRequest {
    constructor(apiCall) {
        this._apiCall = apiCall;
        this.data = null;
        this.error = null;
        this.loading = false;
        this.called = false;
    }
    async execute(...args) {
        this.loading = true;
        this.error = null;
        this.called = true;
        try {
            const result = await this._apiCall(...args);
            this.data = result;
            return result;
        } catch (e) {
            this.error = e;
            throw e;
        } finally {
            this.loading = false;
        }
    }
    get isLoading() { return this.loading; }
    get isSuccess() { return this.called && !this.loading && !this.error; }
}

class HikarinApi {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
        this.auth = new AuthAPI(this);
        this.config = new ConfigAPI(this);
        this.collections = new CollectionsAPI(this); // Renamed alias for 'Forms'
        this.media = new MediaAPI(this);
        this.pages = new PagesAPI(this);
        this.users = new UsersAPI(this);
        this.files = new FileAPI(this); 
    }

    async _request(method, endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method: method.toUpperCase(),
            headers: {},
            credentials: 'include',
            ...options
        };

        if (options.body && !(options.body instanceof FormData)) {
            config.headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(options.body);
        }
        if (!(options.body instanceof FormData)) config.headers['Accept'] = 'application/json';

        const response = await fetch(url, config);
        
        if (!response.ok) {
            let errorDetail = null;
            let errorMessage = `API Error: ${response.statusText}`;
            try {
                const body = await response.json();
                errorDetail = body;
                errorMessage = body.detail || errorMessage;
            } catch (e) {}
            throw new HikarinApiError(errorMessage, response.status, errorDetail);
        }
        
        if (response.status === 204) return null;
        
        const contentType = response.headers.get('content-type');
        return (contentType && contentType.includes('application/json')) ? response.json() : response;
    }
}

// --- API Sub-Classes ---

// "Forms" backend = "Collections" frontend
class CollectionsAPI {
    constructor(client) { this._client = client; }
    
    // Schema Management (Defining the Tables)
    list(tag=null) { 
        const q = tag ? `?tag=${tag}` : '';
        return new ApiRequest(() => this._client._request('GET', `/forms/list${q}`)); 
    }
    get(slug) { return new ApiRequest(() => this._client._request('GET', `/forms/${slug}`)); }
    create(data) { return new ApiRequest(() => this._client._request('POST', '/forms/', { body: data })); }
    update(slug, data) { return new ApiRequest(() => this._client._request('PUT', `/forms/${slug}`, { body: data })); }
    delete(slug) { return new ApiRequest(() => this._client._request('DELETE', `/forms/${slug}`)); }
    
    // Record Management (The actual Data/Submissions)
    listRecords(slug, skip=0, limit=100) {
        return new ApiRequest(() => this._client._request('GET', `/forms/${slug}/submissions?skip=${skip}&limit=${limit}`));
    }
    createRecord(slug, payload) {
        // payload matches SubmissionCreate: { data: {...}, custom: {...} }
        return new ApiRequest(() => this._client._request('POST', `/forms/${slug}/submit`, { body: payload }));
    }
    updateRecord(slug, id, payload) {
        return new ApiRequest(() => this._client._request('PUT', `/forms/${slug}/submissions/${id}`, { body: payload }));
    }
    deleteRecord(slug, id) {
        return new ApiRequest(() => this._client._request('DELETE', `/forms/${slug}/submissions/${id}`));
    }
}

class PagesAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', `/page/list`)); }
    get(slug) { return new ApiRequest(() => this._client._request('GET', `/page/${slug}`)); }
    create() { return new ApiRequest((data) => this._client._request('POST', '/page/', { body: data })); }
    update() { return new ApiRequest((slug, data) => this._client._request('PUT', `/page/${slug}`, { body: data })); }
    delete() { return new ApiRequest((slug) => this._client._request('DELETE', `/page/${slug}`)); }
}

class UsersAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', '/users/')); }
    create() { return new ApiRequest((data) => this._client._request('POST', '/users/', { body: data })); }
    update(u, d) { return new ApiRequest(() => this._client._request('PUT', `/users/${u}`, { body: d })); }
    delete(u) { return new ApiRequest(() => this._client._request('DELETE', `/users/${u}`)); }
    roles() { return new ApiRequest(() => this._client._request('GET', '/users/roles')); }
}

class MediaAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', '/media/')); }
    upload() {
        return new ApiRequest((files) => {
            const fd = new FormData();
            for (const f of files) fd.append('files', f);
            return this._client._request('POST', '/media/', { body: fd });
        });
    }
    delete() { return new ApiRequest((f) => this._client._request('DELETE', `/media/${f}`)); }
}

class FileAPI {
    constructor(client) { this._client = client; }

    // POST /file/
    // Expects a single File object (from input.files[0])
    upload() {
        return new ApiRequest((fileObj) => {
            const fd = new FormData();
            fd.append('file', fileObj); 
            return this._client._request('POST', '/file/', { body: fd });
        });
    }

    // DELETE /file/{filename}
    delete(filename) { 
        return new ApiRequest(() => this._client._request('DELETE', `/file/${filename}`)); 
    }
}

class ConfigAPI {
    constructor(client) { this._client = client; }
    get() { return new ApiRequest(() => this._client._request('GET', '/config/')); }
    update() { return new ApiRequest((d) => this._client._request('POST', '/config/', { body: d })); }
}

class AuthAPI {
    constructor(client) { this._client = client; }
    login(u, p, r=false) {
        return new ApiRequest(() => {
            const fd = new FormData();
            fd.append('username', u); fd.append('password', p); fd.append('remember_me', String(r));
            return this._client._request('POST', '/auth/login', { body: fd });
        });
    }
    logout() { return new ApiRequest(() => this._client._request('POST', '/auth/logout')); }
}

// ===================================================================
//  ALPINE.JS - UNIVERSAL MANAGERS
// ===================================================================

const hikarinApi = new HikarinApi();

document.addEventListener('alpine:init', () => {
    Alpine.magic('api', () => hikarinApi);

        Alpine.store('notifications', {
        items: [],
        
        // Helper: Success
        success(title, message = '') {
            this.add('success', title, message);
        },

        // Helper: Error (Smart Parser)
        error(title, errorObj = null) {
            let message = "Something went wrong.";
            
            if (typeof errorObj === 'string') {
                message = errorObj;
            } else if (errorObj && errorObj.detail) {
                // Hikarin/FastAPI error format
                message = errorObj.detail;
            } else if (errorObj && errorObj.message) {
                // JS Error object
                message = errorObj.message;
            }
            
            this.add('error', title, message);
        },

        // Helper: Info
        info(title, message = '') {
            this.add('info', title, message);
        },

        // Internal: Add to queue
        add(type, title, message) {
            const id = Date.now();
            this.items.push({ id, type, title, message });
            
            // Auto-remove after 4 seconds
            setTimeout(() => {
                this.remove(id);
            }, 4000);
        },

        // Internal: Remove
        remove(id) {
            this.items = this.items.filter(item => item.id !== id);
        }
    });

    // ------------------------------------------------------------------
    // SCHEMA MANAGER (Admin)
    // "I want to design a new Table (e.g. Cafe Menu)"
    // ------------------------------------------------------------------
    Alpine.data('schemaManager', () => ({
        collections: [],
        modalOpen: false,
        mode: 'create', // create | edit
        
        // The Definition
        def: {
            title: '', 
            slug: '', 
            description: '', 
            tags: [], 
            schemaString: '{\n  "type": "object",\n  "properties": {\n    "item_name": {"type": "string"},\n    "price": {"type": "number"}\n  }\n}'
        },
        targetSlug: '',
        tagInput: '',

        async init() { await this.refresh(); },
        async refresh() {
            const req = await this.$api.collections.list().execute();
            this.collections = req;
        },

        openCreate() {
            this.def = { title: '', slug: '', description: '', tags: [], schemaString: '{\n  "type": "object",\n  "properties": {\n    "field_name": {"type": "string"}\n  }\n}' };
            this.mode = 'create';
            this.modalOpen = true;
        },

        openEdit(item) {
            this.mode = 'edit';
            this.targetSlug = item.slug;
            this.def.title = item.title;
            this.def.slug = item.slug;
            this.def.description = item.description;
            this.def.tags = item.tags ? [...item.tags] : [];
            this.def.schemaString = JSON.stringify(item.schema || {}, null, 2);
            this.modalOpen = true;
        },

        generateSlug() {
            if(this.mode === 'create') this.def.slug = this.def.title.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
        },

        addTag() { if(this.tagInput) this.def.tags.push(this.tagInput); this.tagInput = ''; },
        removeTag(i) { this.def.tags.splice(i, 1); },

        async save() {
            let parsedSchema;
            try { parsedSchema = JSON.parse(this.def.schemaString); } catch(e) { alert("Invalid JSON Schema"); return; }
            
            const payload = {
                title: this.def.title,
                slug: this.def.slug,
                description: this.def.description,
                tags: this.def.tags,
                schema: parsedSchema, // Pydantic alias='schema'
                custom: {}
            };

            try {
                if(this.mode === 'create') await this.$api.collections.create().execute(payload);
                else await this.$api.collections.update().execute(this.targetSlug, payload);
                this.modalOpen = false;
                this.refresh();
            } catch(e) { Alpine.store('notifications').error('Create Form Failed', e); ; }
            Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
        },
        
        async deleteCollection(slug) {
            if(!confirm("Delete this entire collection and all its data?")) return;
            await this.$api.collections.delete(slug).execute();
            this.refresh();
        }
    }));

    // ------------------------------------------------------------------
    // DATA MANAGER (Universal)
    // "I want to View/Edit the Cafe Menu"
    // Works for both Admin Panel and Public Pages (if authorized)
    // ------------------------------------------------------------------
    Alpine.data('dataManager', (collectionSlug) => ({
        slug: collectionSlug,
        definition: null, // Stores the Schema (columns)
        records: [],      // Stores the Data (rows)
        headers: [],      // Dynamic table headers based on Schema properties
        
        // Editor State
        editorOpen: false,
        editorMode: 'create', // create | edit
        targetId: null,
        
        // The Record currently being edited
        record: {
            data: {}, // Dynamic JSON fields
            custom: {} // Metadata
        },

        async init() {
            // 1. Get Definition to build UI
            const defReq = await this.$api.collections.get(this.slug).execute();
            this.definition = defReq;
            
            // 2. Extract Headers from Schema for the Table View
            if(this.definition.schema && this.definition.schema.properties) {
                this.headers = Object.keys(this.definition.schema.properties);
            }

            // 3. Load Data
            await this.refreshData();
        },

        async refreshData() {
            const dataReq = await this.$api.collections.listRecords(this.slug).execute();
            this.records = dataReq;
        },

        // --- Record Editor Logic ---

        openCreate() {
            this.editorMode = 'create';
            this.record = { data: {}, custom: {} };
            // Pre-fill keys from schema for better UI experience
            this.headers.forEach(h => this.record.data[h] = ''); 
            this.editorOpen = true;
        },

        openEdit(row) {
            this.editorMode = 'edit';
            this.targetId = row.id;
            // Deep copy to avoid mutating list view while editing
            this.record = JSON.parse(JSON.stringify(row));
            this.editorOpen = true;
        },

        async saveRecord() {
            const payload = {
                data: this.record.data,
                custom: this.record.custom,
                tags: [] 
            };

            try {
                if(this.editorMode === 'create') {
                    await this.$api.collections.createRecord(this.slug, payload).execute();
                } else {
                    await this.$api.collections.updateRecord(this.slug, this.targetId, payload).execute();
                }
                this.editorOpen = false;
                this.refreshData();
            } catch(e) { Alpine.store('notifications').error('Submission Failed', e);  }
        },

        async deleteRecord(id) {
            if(!confirm("Delete this entry?")) return;
            await this.$api.collections.deleteRecord(this.slug, id).execute();
            this.refreshData();
        }
    }));

    // ------------------------------------------------------------------
    // PAGE MANAGER
    // ------------------------------------------------------------------
    Alpine.data('pageManager', () => ({
        pages: [],
        search: '',
        isLoading: false,
        
        // Modal State
        modalOpen: false,
        deleteModalOpen: false,
        mode: 'create', // 'create' | 'edit'
        targetSlug: '',

        // Form Data
        form: {
            title: '',
            slug: '',
            description: '',
            thumb: '',
            type: 'markdown', // markdown | html
            tagInput: '',
            tags: [],
            customFields: [] // Array of {k, v} objects for UI
        },

        async init() {
            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                // Assuming $api is available via Alpine.magic from Hikarin
                this.pages = await this.$api.pages.list().execute();
            } catch(e) {
                console.error(e);
                Alpine.store('toasts').add("Failed to load pages", "error");
            } finally {
                this.isLoading = false;
            }
        },

        // --- Form Logic ---

        openCreate() {
            this.mode = 'create';
            this.resetForm();
            this.modalOpen = true;
        },

        openEdit(page) {
            this.mode = 'edit';
            this.targetSlug = page.slug;
            
            // Map API data to Form
            this.form.title = page.title;
            this.form.slug = page.slug;
            this.form.type = page.type || 'markdown';
            this.form.thumb = page.thumb || '';
            this.form.description = page.description || (page.custom ? page.custom.description : '') || '';
            this.form.tags = page.tags ? [...page.tags] : [];
            
            // Handle Custom Fields (Convert Object -> Array)
            this.form.customFields = [];
            if (page.custom) {
                Object.entries(page.custom).forEach(([k, v]) => {
                    if(k !== 'description') this.form.customFields.push({k, v});
                });
            }
            
            this.modalOpen = true;
        },

        resetForm() {
            this.form = {
                title: '', slug: '', description: '', thumb: '',
                type: 'markdown', tagInput: '', tags: [], customFields: []
            };
        },

        generateSlug() {
            if (this.mode === 'create') {
                this.form.slug = this.form.title.toLowerCase()
                    .replace(/[^\w\s-]/g, '')
                    .replace(/\s+/g, '-');
            }
        },

        // --- Tag & Field Logic ---

        addTag() {
            const val = this.form.tagInput.trim();
            if (val && !this.form.tags.includes(val)) {
                this.form.tags.push(val);
            }
            this.form.tagInput = '';
        },
        removeTag(index) { this.form.tags.splice(index, 1); },

        addCustomField() { this.form.customFields.push({k: '', v: ''}); },
        removeCustomField(index) { this.form.customFields.splice(index, 1); },

        // --- Actions ---

        async uploadThumbnail(e) {
            const files = e.target.files;
            if(files.length > 0) {
                try {
                    const req = this.$api.media.upload();
                    const res = await req.execute(files);
                    if(res.files && res.files.length > 0) {
                        this.form.thumb = '/media/' + res.files[0].saved_as;
                    }
                } catch(err) { 
                    Alpine.store('notifications').error('Upload Failed', err); ; 
                }
            }
        },

async save() {
            // 1. Prepare Metadata
            const customObj = { description: this.form.description };
            this.form.customFields.forEach(f => { if(f.k) customObj[f.k] = f.v; });

            // 2. Construct Payload
            const payload = {
                title: this.form.title,
                slug: this.form.slug,
                type: this.form.type,
                thumb: this.form.thumb,
                tags: this.form.tags,
                custom: customObj
            };

            // Debug: Check console to ensure this object is not empty
            console.log("Submitting Payload:", payload);

            try {
                if(this.mode === 'create') {
                    // Create takes 1 argument (data)
                    // Correct: .create().execute(payload)
                    await this.$api.pages.create().execute(payload);
                } else {
                    // Update takes 2 arguments (slug, data)
                    // ERROR WAS HERE: We must pass args to execute(), not update()
                    await this.$api.pages.update().execute(this.targetSlug, payload);
                }

                // Success
                this.modalOpen = false;
                Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
                this.refresh();
                
            } catch(e) {
                console.error("Save failed:", e);
                Alpine.store('notifications').error('Save Failed', e); ;
            }
        },

        confirmDelete(slug) {
            this.targetSlug = slug;
            this.deleteModalOpen = true;
        },

        async doDelete() {
            try {
                await this.$api.pages.delete(this.targetSlug).execute();
                this.deleteModalOpen = false;
                this.refresh();
            } catch(e) {
                Alpine.store('notifications').error('Delete Failed', e); ;
            }
        },

        // Helper for filter
        filteredPages() {
            if(!this.search) return this.pages;
            const s = this.search.toLowerCase();
            return this.pages.filter(p => p.title.toLowerCase().includes(s) || p.slug.includes(s));
        }
    }));

// ------------------------------------------------------------------
    // USER MANAGER (Split-Pane UI Version)
    // ------------------------------------------------------------------
    Alpine.data('userManager', () => ({
        view: 'users', // 'users' | 'roles'
        isLoading: false,
        
        // Data
        users: [],
        roles: [], // Array of objects
        
        // Selection State (for Roles Split Pane)
        selectedRole: null, 

        // Modals
        userModalOpen: false,
        passwordModalOpen: false,
        deleteModalOpen: false,
        isEditingUser: false,

        // Forms
        userForm: { username: '', display_name: '', role: 'viewer', disabled: false, password: '' },
        passwordForm: { username: '', new_password: '' },
        roleForm: { role_name: '', permissions: [] },
        deleteTarget: { type: '', id: '' },

        // Static Data: Permission Categories
        permCategories: [
            {
                name: 'Administrator',
                perms: [
                    { key: '*', label: 'Administrator', desc: 'Grants full unrestricted access to all system features, settings, content, and tools.' }

                ]
            },
            {
                name: 'Forms & Submissions',
                perms: [
                    { key: 'form:create', label: 'Create Forms', desc: 'Allows creating new forms, including defining fields, settings, and behavior.' },
{ key: 'form:read', label: 'View Forms', desc: 'Allows viewing existing forms and their configuration.' },
{ key: 'form:update', label: 'Edit Forms', desc: 'Allows editing or modifying existing forms and their settings.' },
{ key: 'form:delete', label: 'Delete Forms', desc: 'Allows deleting forms entirely from the system.' },

{ key: 'submission:create', label: 'Create Submissions (Override)', desc: 'Allows creating form submissions even when the form’s own access rules would normally prevent it.' },
{ key: 'submission:read', label: 'View Submissions (Override)', desc: 'Allows viewing any form submissions regardless of the form’s internal permission rules.' },
{ key: 'submission:update', label: 'Edit Submissions (Override)', desc: 'Allows editing any form submission even if role-based or form-level rules would normally block it.' },
{ key: 'submission:delete', label: 'Delete Submissions (Override)', desc: 'Allows deleting any form submission regardless of the form’s access restrictions.' },

                ]
            },
            {
                name: 'Media Library',
                perms: [
                    { key: 'media:create', label: 'Upload Media', desc: 'Allows uploading new media files into the media library.' },
{ key: 'media:read', label: 'View Media Library', desc: 'Allows browsing and viewing items in the media library.' },
{ key: 'media:update', label: 'Edit Media Metadata', desc: 'Allows editing media details such as titles, descriptions, and tags.' },
{ key: 'media:delete', label: 'Delete Media', desc: 'Allows permanently deleting media files from the library.' },

                ]
            },
            {
                name: 'Blog System',
                perms: [
                  { key: 'blog:create', label: 'Create Posts', desc: 'Allows writing and publishing new blog posts.' },
{ key: 'blog:read', label: 'Read Posts', desc: 'Allows access to view all blog posts in the system.' },
{ key: 'blog:update', label: 'Edit Posts', desc: 'Allows modifying existing blog posts.' },
{ key: 'blog:delete', label: 'Delete Posts', desc: 'Allows deleting blog posts permanently.' },

                ]
            },
            {
                name: 'Pages & Content',
                perms: [
                    { key: 'page:create', label: 'Create Pages', desc: 'Allows creating new pages in the CMS.' },
{ key: 'page:read', label: 'View Pages', desc: 'Allows viewing all pages within the CMS.' },
{ key: 'page:update', label: 'Edit Pages', desc: 'Allows modifying page content, metadata, and settings.' },
{ key: 'page:delete', label: 'Delete Pages', desc: 'Allows deleting pages from the CMS.' },

                ]
            },
            {
                name: 'System & AI',
                perms: [
                  { key: 'config:read', label: 'View Config', desc: 'Allows viewing system configuration values without exposing sensitive secrets.' },
{ key: 'config:update', label: 'Edit Config', desc: 'Allows editing or updating system configuration values.' },

{ key: 'aina', label: 'Access Aina (HTML AI)', desc: 'Allows using Aina, the HTML-based AI assistant.' },
{ key: 'asta', label: 'Access Asta (Markdown AI)', desc: 'Allows using Asta, the Markdown Editor.' },

                ]
            }
        ],

        async init() {
            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                const [uReq, rReq] = await Promise.all([
                    this.$api.users.list().execute(),
                    this.$api.users.roles().execute()
                ]);
                
                this.users = uReq || [];
                
                // Handle Dictionary -> Array conversion for Roles
                if (rReq && !Array.isArray(rReq) && typeof rReq === 'object') {
                    this.roles = Object.entries(rReq).map(([k, v]) => ({ role_name: k, permissions: v }));
                } else {
                    this.roles = rReq || [];
                }

                // Reselect role if active to update permissions visual state
                if(this.selectedRole) {
                    const found = this.roles.find(r => r.role_name === this.selectedRole.role_name);
                    if(found) this.selectRole(found);
                }

            } catch(e) { console.error(e); }
            finally { this.isLoading = false; }
        },

        // --- USER LOGIC ---

        openCreateUser() {
            this.isEditingUser = false;
            const firstRole = this.roles.length > 0 ? this.roles[0].role_name : 'viewer';
            this.userForm = { username: '', display_name: '', role: firstRole, disabled: false, password: '' };
            this.userModalOpen = true;
        },

        openEditUser(user) {
            this.isEditingUser = true;
            this.userForm = { 
                username: user.username,
                display_name: user.display_name,
                role: user.role,
                disabled: user.disabled,
                password: '' 
            };
            this.userModalOpen = true;
        },

        openPasswordModal(user) {
            this.passwordForm = { username: user.username, new_password: '' };
            this.passwordModalOpen = true;
        },

        async saveUser() {
            try {
                const payload = {
                    display_name: this.userForm.display_name,
                    role: this.userForm.role,
                    disabled: this.userForm.disabled
                };

                if (this.isEditingUser) {
                    await this.$api.users.update(this.userForm.username, payload).execute();
                } else {
                    payload.username = this.userForm.username;
                    payload.password = this.userForm.password;
                    await this.$api.users.create().execute(payload);
                }
                this.userModalOpen = false;
                this.refresh();
            } catch(e) { Alpine.store('notifications').error('Save Failed', e);  }
        },

        async changePassword() {
            // Assuming a custom endpoint or generic update
            try {
                // If your API has a specific endpoint, use that. 
                // Otherwise, some systems allow password update via standard PUT if permissions allow.
                // We'll try the standard update first.
                await this.$api.users.update(this.passwordForm.username, { 
                    password: this.passwordForm.new_password 
                }).execute();
                
                this.passwordModalOpen = false;
                alert('Password updated');
            } catch(e) { Alpine.store('notifications').error('Update Password Failed', e);  }
        },

        // --- ROLE LOGIC (Split Pane) ---

        selectRole(role) {
            this.selectedRole = role; // Reference for UI highlight
            this.roleForm = {
                role_name: role.role_name,
                permissions: [...role.permissions] // Deep copy perms
            };
        },

        createNewRole() {
            const name = 'New Role ' + (this.roles.length + 1);
            const newRole = { role_name: name, permissions: [] };
            this.roles.push(newRole);
            this.selectRole(newRole);
        },

        togglePermission(key) {
            if (this.roleForm.permissions.includes(key)) {
                this.roleForm.permissions = this.roleForm.permissions.filter(p => p !== key);
            } else {
                this.roleForm.permissions.push(key);
            }
        },

        async saveRole() {
            if(!this.selectedRole) return;
            try {
                const payload = {
                    role_name: this.roleForm.role_name,
                    permissions: this.roleForm.permissions
                };
                
                // Using generic POST to /users/roles/
                await this.$api._request('POST', '/users/roles/', { body: payload });
                
                // Visual feedback
                const btn = document.getElementById('save-role-btn');
                const oldText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i> Saved';
                setTimeout(() => btn.innerHTML = oldText, 2000);

                this.refresh();
            } catch(e) { Alpine.store('notifications').error('Save Failed', e); }
        },

        // --- SHARED DELETE LOGIC ---

        confirmDelete(type, id) {
            this.deleteTarget = { type, id };
            this.deleteModalOpen = true;
        },

        async doDelete() {
            try {
                if (this.deleteTarget.type === 'user') {
                    await this.$api.users.delete(this.deleteTarget.id).execute();
                } else {
                    await this.$api._request('DELETE', `/users/roles/${this.deleteTarget.id}`);
                    // If we deleted the currently viewed role, deselect
                    if(this.selectedRole && this.selectedRole.role_name === this.deleteTarget.id) {
                        this.selectedRole = null;
                    }
                }
                this.deleteModalOpen = false;
                this.refresh();
            } catch(e) { Alpine.store('notifications').error('Delete Failed', e); }
        }
    }));

    Alpine.data('adminShell', () => ({
        sidebarOpen: true,
        currentPath: window.location.pathname,

        init() {
            // Listen for HTMX navigation events to update the active tab
            document.body.addEventListener('htmx:afterSwap', (e) => {
                // You might need to adjust how you track path based on your backend URL structure
                this.currentPath = e.detail.pathInfo.requestPath;
            });
        },

        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },

        // Helper to set active class on sidebar links
        isActive(path) {
            // Simple check: is the current path inside the link path?
            return this.currentPath.includes(path);
        }
    }));

// ------------------------------------------------------------------
    // MEDIA MANAGER
    // ------------------------------------------------------------------
    Alpine.data('mediaManager', () => ({
        files: [],      // Physical files
        metaMap: {},    // Map: filename -> { title, desc, id }
        isLoading: false,
        
        // UI State
        activeTab: 'all', // all | unregistered
        uploadModalOpen: false,
        detailsModalOpen: false,

        // Details Form
        targetFilename: '',
        targetId: null, // If null, it's unregistered
        form: { title: '', description: '', link: '' },
        
        // Upload Form
        uploadFile: null,
        uploadMeta: { title: '', description: '' },
        isUploading: false,

        async init() {
            await this.ensureSchema();
            await this.refresh();
        },

        // Auto-create the 'media-data' collection if it doesn't exist
        async ensureSchema() {
            try {
                await this.$api.collections.get('media-data').execute();
            } catch (e) {
                if (e.status === 404) {
                    console.log("Initializing Media Schema...");
                    const payload = {
                        slug: "media-data",
                        title: "Media Metadata",
                        description: "System metadata for uploaded files",
                        tags: ["system", "read"],
                        schema: { fields: [
                            { name: "saved_filename", label: "Filename", type: "text" },
                            { name: "friendly_name", label: "Title", type: "text" },
                            { name: "description", label: "Desc", type: "textarea" },
                            { name: "public_link", label: "Link", type: "text" }
                        ]}
                    };
                    await this.$api.collections.create(payload).execute();
                }
            }
        },

        async refresh() {
            this.isLoading = true;
            try {
                // 1. Get Physical Files
                const filesReq = await this.$api.media.list().execute();
                
                // 2. Get Metadata
                let metaList = [];
                try {
                    metaList = await this.$api.collections.listRecords('media-data').execute();
                } catch(e) {} // It's okay if empty

                // 3. Merge
                this.metaMap = {};
                metaList.forEach(item => {
                    // Assuming data structure from API
                    if(item.data && item.data.saved_filename) {
                        this.metaMap[item.data.saved_filename] = {
                            id: item.id,
                            title: item.data.friendly_name,
                            description: item.data.description
                        };
                    }
                });

                this.files = filesReq;

            } catch (e) {
                console.error(e);
            } finally {
                this.isLoading = false;
            }
        },

        // --- Computed Helper ---
        getDisplayData(filename) {
            if (this.metaMap[filename]) {
                return {
                    isRegistered: true,
                    title: this.metaMap[filename].title,
                    desc: this.metaMap[filename].description
                };
            }
            return {
                isRegistered: false,
                title: filename, // Fallback
                desc: 'Unregistered'
            };
        },

        // --- Actions ---

        openUpload() {
            this.uploadFile = null;
            this.uploadMeta = { title: '', description: '' };
            this.uploadModalOpen = true;
            // Reset file input manually if needed
            const input = document.getElementById('mm-file-input');
            if(input) input.value = '';
        },

        handleFileSelect(e) {
            const file = e.target.files[0];
            if(file) {
                this.uploadFile = file;
                // Auto-fill title
                if(!this.uploadMeta.title) {
                    this.uploadMeta.title = file.name.split('.')[0];
                }
            }
        },

        async doUpload() {
            if(!this.uploadFile) return;
            this.isUploading = true;
            
            try {
                // 1. Upload File
                const res = await this.$api.media.upload().execute([this.uploadFile]);
                const savedFile = res.files[0];
                
                // 2. Register Metadata
                const payload = {
                    data: {
                        saved_filename: savedFile.saved_as,
                        friendly_name: this.uploadMeta.title,
                        description: this.uploadMeta.description,
                        public_link: '/media/' + savedFile.saved_as
                    }
                };
                
                // createRecord(slug, payload)
                await this.$api.collections.createRecord('media-data', payload).execute();
                
                this.uploadModalOpen = false;
                this.refresh();

            } catch(e) {
                Alpine.store('notifications').error('Upload Failed', e); ;
            } finally {
                this.isUploading = false;
            }
        },

        openDetails(filename) {
            this.targetFilename = filename;
            this.form.link = window.location.origin + '/media/' + filename;
            
            const meta = this.metaMap[filename];
            if (meta) {
                this.targetId = meta.id;
                this.form.title = meta.title;
                this.form.description = meta.description;
            } else {
                this.targetId = null;
                this.form.title = filename.split('.')[0];
                this.form.description = '';
            }
            
            this.detailsModalOpen = true;
        },

        async saveDetails() {
            const payload = {
                data: {
                    saved_filename: this.targetFilename,
                    friendly_name: this.form.title,
                    description: this.form.description,
                    public_link: '/media/' + this.targetFilename
                }
            };

            try {
                if (this.targetId) {
                    // Update existing metadata
                    await this.$api.collections.updateRecord('media-data', this.targetId, payload).execute();
                } else {
                    // Create new metadata for orphan
                    await this.$api.collections.createRecord('media-data', payload).execute();
                }
                this.detailsModalOpen = false;
                this.refresh();
            } catch(e) {
                Alpine.store('notifications').error('Error Saving Metadata', e); 
            }
        },

        async deleteMedia() {
            if(!confirm("Permanently delete this file?")) return;
            
            try {
                // 1. Delete Physical
                await this.$api.media.delete(this.targetFilename).execute();
                
                // 2. Delete Metadata (if exists)
                if (this.targetId) {
                    await this.$api.collections.deleteRecord('media-data', this.targetId).execute();
                }
                
                this.detailsModalOpen = false;
                this.refresh();
            } catch(e) {
                Alpine.store('notifications').error('Error Deleting File', e); 
            }
        },

        copyLink() {
            navigator.clipboard.writeText(this.form.link);
            // Optional: visual feedback handled in UI via x-data local state
        }
    }));

    // ------------------------------------------------------------------
    // FORM / COLLECTION MANAGER
    // ------------------------------------------------------------------
    Alpine.data('formManager', () => ({
        forms: [],
        isLoading: false,
        activeTab: 'settings', // settings | builder | submissions
        
        // Modal State
        modalOpen: false,
        mode: 'create',
        currentSlug: '',
        
        // Form Structure
        form: {
            title: '',
            slug: '',
            description: '',
            tags: [],
            tagInput: '',
            fields: [] // Flat array for easier Alpine editing
        },

        // Submissions Data
        submissions: [],
        subsLoading: false,

        async init() {
            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                this.forms = await this.$api.collections.list().execute();
            } catch (e) { console.error(e); }
            this.isLoading = false;
        },

        // --- Slug Logic ---
        handleTitleInput() {
            if (this.mode === 'create') {
                this.form.slug = this.form.title
                    .toLowerCase()
                    .trim()
                    .replace(/\s+/g, '_')           // Spaces to underscores
                    .replace(/[^\w]/g, '');         // Remove non-word chars
            }
        },

        sanitizeSlug() {
            this.form.slug = this.form.slug
                .toLowerCase()
                .replace(/\s+/g, '_')
                .replace(/[^\w]/g, '');
        },

        // --- Field Builder ---
        addField() {
            this.form.fields.push({ 
                name: '', 
                label: '', 
                type: 'text', 
                required: false 
            });
        },

        removeField(index) {
            this.form.fields.splice(index, 1);
        },

        updateFieldSlug(index) {
            // Auto-gen field name from label if name is empty
            if (!this.form.fields[index].name) {
                this.form.fields[index].name = this.form.fields[index].label
                    .toLowerCase()
                    .replace(/\s+/g, '_')
                    .replace(/[^\w]/g, '');
            }
        },

        // --- Tag Logic ---
        addTag() {
            let t = this.form.tagInput.trim().toLowerCase();
            if (t && !this.form.tags.includes(t)) this.form.tags.push(t);
            this.form.tagInput = '';
        },

        // --- Actions ---
        openCreate() {
            this.mode = 'create';
            this.activeTab = 'settings';
            this.form = { title: '', slug: '', description: '', tags: [], tagInput: '', fields: [] };
            this.addField(); // Start with one field
            this.modalOpen = true;
        },

        async openEdit(item) {
            this.mode = 'edit';
            this.activeTab = 'settings';
            this.currentSlug = item.slug;
            
            this.form = {
                title: item.title,
                slug: item.slug,
                description: item.description || '',
                tags: item.tags || [],
                tagInput: '',
                // Convert JSON Schema properties back to our flat array
                fields: item.schema && item.schema.fields ? [...item.schema.fields] : []
            };
            this.modalOpen = true;
        },

        async save() {
            this.sanitizeSlug();
            const payload = {
                title: this.form.title,
                slug: this.form.slug,
                description: this.form.description,
                tags: this.form.tags,
                schema: { fields: this.form.fields },
                custom: {}
            };

            // Debug Payload
            console.log("Saving Form:", payload);

            try {
                if (this.mode === 'create') {
                    // FIX: CollectionsAPI expects payload in the first call, not execute()
                    await this.$api.collections.create(payload).execute();
                } else {
                    // FIX: CollectionsAPI expects slug AND payload in the first call
                    await this.$api.collections.update(this.currentSlug, payload).execute();
                }
                
                this.modalOpen = false;
                Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
                this.refresh();
                
            } catch (e) { 
                console.error(e);
                Alpine.store('notifications').error('Could Not Save Form', e); 
            }
        },

        async deleteForm(slug) {
            if (!confirm("Delete this form and all data?")) return;
            await this.$api.collections.delete(slug).execute();
            this.refresh();
        },

        // --- Submissions ---
        async loadSubmissions() {
            this.subsLoading = true;
            try {
                this.submissions = await this.$api.collections.listRecords(this.currentSlug).execute();
            } catch (e) { console.error(e); }
            this.subsLoading = false;
        }
    }));

    // ------------------------------------------------------------------
    // CONFIG MANAGER
    // ------------------------------------------------------------------
    Alpine.data('configManager', () => ({
        isLoading: false,
        isSaving: false,
        
        form: {
            ai_endpoint: '',
            base_llm: '',
            ai_key: '',
            temperature: 0.7,
            system_note: ''
        },

        async init() {
            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                // Fetch current config
                const res = await this.$api.config.get().execute();
                
                // Map to form
                this.form.ai_endpoint = res.ai_endpoint || '';
                this.form.base_llm = res.base_llm || '';
                this.form.temperature = res.temperature !== undefined ? res.temperature : 0.7;
                this.form.system_note = res.system_note || '';
                
                // Never populate the key field for security, it stays blank implies "no change"
                this.form.ai_key = ''; 
            } catch (e) {
                console.error("Config Load Error", e);
            } finally {
                this.isLoading = false;
            }
        },

        async save() {
            this.isSaving = true;
            
            // Clone form to avoid mutating UI state during save
            const payload = { ...this.form };

            // If key is empty, don't send it (backend should treat this as "keep existing")
            if (!payload.ai_key || payload.ai_key.trim() === '') {
                delete payload.ai_key;
            }

            try {
                await this.$api.config.update().execute(payload);
                
                // Visual Feedback
                const btn = document.getElementById('save-config-btn');
                const oldHTML = btn.innerHTML;
                btn.innerHTML = `<i class="fas fa-check mr-2"></i> Saved!`;
                btn.classList.remove('bg-slate-900', 'hover:bg-slate-800');
                btn.classList.add('bg-green-600', 'hover:bg-green-700');
                
                setTimeout(() => {
                    btn.innerHTML = oldHTML;
                    btn.classList.add('bg-slate-900', 'hover:bg-slate-800');
                    btn.classList.remove('bg-green-600', 'hover:bg-green-700');
                }, 2000);

                // Reload to confirm values
                Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
                await this.refresh();

            } catch (e) {
                Alpine.store('notifications').error('Failed to Save Configuration', e); 
            } finally {
                this.isSaving = false;
                Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
            }
        }
    }));

    // ------------------------------------------------------------------
    // FILE MANAGER (Compact List)
    // ------------------------------------------------------------------
    Alpine.data('fileManager', () => ({
        files: [],
        isLoading: false,
        search: '',
        
        // Upload State
        uploadModalOpen: false,
        isUploading: false,
        uploadFile: null,
        uploadMeta: { title: '', description: '' },

        // Details/Edit State
        detailsModalOpen: false,
        editForm: { id: null, title: '', description: '', filename: '', size: '', link: '' },

        async init() {
            await this.ensureSchema();
            await this.refresh();
        },

        // 1. Ensure the 'file-data' registry exists
        async ensureSchema() {
            try {
                await this.$api.collections.get('file-data').execute();
            } catch (e) {
                if (e.status === 404) {
                    const payload = {
                        slug: "file-data",
                        title: "File Registry",
                        description: "Registry for documents and generic files",
                        tags: ["system", "read"],
                        schema: { fields: [
                            { name: "saved_filename", label: "Filename", type: "text" },
                            { name: "friendly_name", label: "Title", type: "text" },
                            { name: "description", label: "Desc", type: "textarea" },
                            { name: "extension", label: "Ext", type: "text" },
                            { name: "size", label: "Size", type: "text" },
                            { name: "public_link", label: "Link", type: "text" }
                        ]}
                    };
                    await this.$api.collections.create(payload).execute();
                }
            }
        },

        async refresh() {
            this.isLoading = true;
            try {
                // We fetch the Registry (metadata), not the raw folder
                this.files = await this.$api.collections.listRecords('file-data').execute();
            } catch(e) { console.error(e); } 
            finally { this.isLoading = false; }
        },

        // --- UPLOAD LOGIC ---
        openUpload() {
            this.uploadFile = null;
            this.uploadMeta = { title: '', description: '' };
            this.uploadModalOpen = true;
            const input = document.getElementById('fm-file-input');
            if(input) input.value = '';
        },

        handleFileSelect(e) {
            const file = e.target.files[0];
            if(file) {
                this.uploadFile = file;
                // Auto-fill title from filename
                if(!this.uploadMeta.title) {
                    this.uploadMeta.title = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
                }
            }
        },

        async doUpload() {
            if(!this.uploadFile) return;
            this.isUploading = true;

            try {
                // CHANGED: Use .files.upload() and pass the single object (not an array)
                const res = await this.$api.files.upload().execute(this.uploadFile);
                
                // Python returns: {"status": "success", "filename": "name.pdf"}
                // We use res.filename
                
                // 2. Register Metadata
                const savedFilename = res.filename;
                const ext = savedFilename.split('.').pop();
                const size = this.formatBytes(this.uploadFile.size);

                const payload = {
                    data: {
                        saved_filename: savedFilename,
                        friendly_name: this.uploadMeta.title,
                        description: this.uploadMeta.description,
                        extension: ext,
                        size: size,
                        public_link: '/file/' + savedFilename
                    }
                };

                await this.$api.collections.createRecord('file-data', payload).execute();
                
                Alpine.store('notifications').success('File Uploaded', `${this.uploadMeta.title} is ready.`);
                this.uploadModalOpen = false;
                this.refresh();

            } catch(e) {
                Alpine.store('notifications').error('Upload Failed', e);
            } finally {
                this.isUploading = false;
            }
        },

        

        // --- EDIT / DELETE LOGIC ---
        openDetails(record) {
            const d = record.data;
            this.editForm = {
                id: record.id,
                title: d.friendly_name,
                description: d.description,
                filename: d.saved_filename,
                size: d.size,
                link: d.public_link || `/media/${d.saved_filename}`
            };
            this.detailsModalOpen = true;
        },

        async saveDetails() {
            const payload = {
                data: {
                    friendly_name: this.editForm.title,
                    description: this.editForm.description,
                    // Keep existing technical data
                    saved_filename: this.editForm.filename,
                    size: this.editForm.size,
                    public_link: this.editForm.link
                }
            };

            try {
                await this.$api.collections.updateRecord('file-data', this.editForm.id, payload).execute();
                Alpine.store('notifications').success('Updated', 'File details saved.');
                this.detailsModalOpen = false;
                this.refresh();
            } catch(e) {
                Alpine.store('notifications').error('Update Failed', e);
            }
        },

        async deleteFile() {
            if(!confirm("Delete this file permanently?")) return;
            try {
                // CHANGED: Use .files.delete()
                // Pass the filename (e.g. "report.pdf") from the editForm
                await this.$api.files.delete(this.editForm.filename).execute();
                
                // 2. Delete Registry Entry
                await this.$api.collections.deleteRecord('file-data', this.editForm.id).execute();
                
                Alpine.store('notifications').success('Deleted', 'File removed.');
                this.detailsModalOpen = false;
                this.refresh();
            } catch(e) {
                Alpine.store('notifications').error('Delete Failed', e);
            }
        },

        // --- HELPERS ---
        filteredFiles() {
            if(!this.search) return this.files;
            const s = this.search.toLowerCase();
            return this.files.filter(f => 
                (f.data.friendly_name && f.data.friendly_name.toLowerCase().includes(s)) || 
                (f.data.saved_filename && f.data.saved_filename.toLowerCase().includes(s))
            );
        },

        copyLink() {
            navigator.clipboard.writeText(window.location.origin + this.editForm.link);
            Alpine.store('notifications').info('Copied', 'Link copied to clipboard');
        },

        formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        getIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            if(['pdf'].includes(ext)) return { icon: 'fa-file-pdf', color: 'text-red-500', bg: 'bg-red-50' };
            if(['doc','docx'].includes(ext)) return { icon: 'fa-file-word', color: 'text-blue-500', bg: 'bg-blue-50' };
            if(['xls','xlsx','csv'].includes(ext)) return { icon: 'fa-file-excel', color: 'text-green-500', bg: 'bg-green-50' };
            if(['zip','rar','7z'].includes(ext)) return { icon: 'fa-file-archive', color: 'text-yellow-600', bg: 'bg-yellow-50' };
            if(['jpg','png','webp'].includes(ext)) return { icon: 'fa-file-image', color: 'text-purple-500', bg: 'bg-purple-50' };
            return { icon: 'fa-file', color: 'text-slate-500', bg: 'bg-slate-100' };
        }
    }));

    // ------------------------------------------------------------------
    // SUBMISSION MANAGER (Standalone Page)
    // ------------------------------------------------------------------
    Alpine.data('submissionManager', () => ({
        slug: '',
        formDef: null,
        submissions: [],
        isLoading: false,
        
        // UI Helpers
        headers: [], // Array of field names
        fields: [],  // Array of field objects {name, type, label} from schema
        
        // Edit State
        modalOpen: false,
        editId: null,
        record: {}, // The dynamic data object

        async init() {
            // 1. Get Slug from URL (?slug=contact)
            const params = new URLSearchParams(window.location.search);
            this.slug = params.get('slug');

            if (!this.slug) {
                Alpine.store('notifications').error('Missing Slug', 'No form slug specified in URL.');
                return;
            }

            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                // A. Fetch Schema (to know columns/fields)
                this.formDef = await this.$api.collections.get(this.slug).execute();
                
                // Parse Schema for Table & Form
                if(this.formDef.schema && this.formDef.schema.fields) {
                    this.fields = this.formDef.schema.fields;
                    this.headers = this.fields.map(f => f.name);
                }

                // B. Fetch Data
                this.submissions = await this.$api.collections.listRecords(this.slug).execute();

                // Fallback: If no schema, guess headers from first record
                if(this.headers.length === 0 && this.submissions.length > 0) {
                    this.headers = Object.keys(this.submissions[0].data || {});
                    // Create dummy fields for the editor
                    this.fields = this.headers.map(h => ({ name: h, label: h, type: 'text' }));
                }

            } catch(e) {
                Alpine.store('notifications').error('Load Error', e);
            } finally {
                this.isLoading = false;
            }
        },

        // --- ACTIONS ---

        openEdit(sub) {
            this.editId = sub.id;
            // Deep copy data to avoid mutating list
            this.record = JSON.parse(JSON.stringify(sub.data));
            // Ensure all schema fields exist in object (even if empty)
            this.fields.forEach(f => {
                if(this.record[f.name] === undefined) this.record[f.name] = '';
            });
            this.modalOpen = true;
        },

        async save() {
            try {
                const payload = {
                    data: this.record,
                    // If your backend requires form_slug or id in body, add it here
                    id: this.editId 
                };

                await this.$api.collections.updateRecord(this.slug, this.editId, payload).execute();
                
                Alpine.store('notifications').success('Saved', 'Submission updated.');
                this.modalOpen = false;
                this.refresh();
            } catch(e) {
                Alpine.store('notifications').error('Save Failed', e);
            }
        },

        async deleteSubmission(id) {
            if(!confirm("Delete this submission?")) return;
            try {
                await this.$api.collections.deleteRecord(this.slug, id).execute();
                Alpine.store('notifications').success('Deleted', 'Record removed.');
                this.refresh();
            } catch(e) {
                Alpine.store('notifications').error('Delete Failed', e);
            }
        },

        downloadCSV() {
            if (this.submissions.length === 0) return;

            // Columns: ID, Created, ...DataKeys
            const cols = ['id', 'created', ...this.headers];
            const rows = [cols.join(',')];

            this.submissions.forEach(s => {
                const row = cols.map(c => {
                    if (c === 'id') return s.id;
                    if (c === 'created') return s.created;
                    // Data fields
                    const val = (s.data && s.data[c] !== undefined) ? s.data[c] : '';
                    return `"${String(val).replace(/"/g, '""')}"`; // Escape quotes
                });
                rows.push(row.join(','));
            });

            const blob = new Blob([rows.join('\n')], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.slug}_submissions.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    }));
});