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
            } catch(e) { alert(e.message); }
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
            } catch(e) { alert(e.message); }
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
        modalOpen: false,
        mode: 'create',
        form: { title: '', slug: '', type: 'markdown', tags: [], customFields: [] },
        targetSlug: '',
        
        async init() { this.refresh(); },
        async refresh() { this.pages = await this.$api.pages.list().execute(); },
        
        openCreate() {
            this.form = { title: '', slug: '', type: 'markdown', tags: [], customFields: [] };
            this.mode = 'create';
            this.modalOpen = true;
        },
        openEdit(p) {
            this.mode = 'edit';
            this.targetSlug = p.slug;
            this.form = { ...p, customFields: [] }; // Populate basics
            if(p.custom) Object.entries(p.custom).forEach(([k,v]) => this.form.customFields.push({k,v}));
            this.modalOpen = true;
        },
        async save() {
            const custom = {};
            this.form.customFields.forEach(f => custom[f.k] = f.v);
            const payload = { ...this.form, custom };
            
            if(this.mode === 'create') await this.$api.pages.create().execute(payload);
            else await this.$api.pages.update(this.targetSlug, payload).execute();
            
            this.modalOpen = false;
            this.refresh();
        },
        async deletePage(slug) {
            if(confirm("Delete?")) { await this.$api.pages.delete(slug).execute(); this.refresh(); }
        }
    }));

    // ------------------------------------------------------------------
    // USER MANAGER
    // ------------------------------------------------------------------
    Alpine.data('userManager', () => ({
        users: [],
        roles: [], // Populated on init
        modalOpen: false,
        mode: 'create',
        form: { username: '', password: '', role: 'viewer', display_name: '' },
        
        async init() { 
            this.refresh();
            try { this.roles = await this.$api.users.roles().execute(); } catch(e) { this.roles = ['admin', 'editor', 'viewer']; }
        },
        async refresh() { this.users = await this.$api.users.list().execute(); },
        
        openCreate() {
            this.form = { username: '', password: '', role: 'viewer', display_name: '' };
            this.mode = 'create';
            this.modalOpen = true;
        },
        openEdit(u) {
            this.mode = 'edit';
            this.form = { ...u, password: '' }; // Don't fill password
            this.modalOpen = true;
        },
        async save() {
            const payload = { ...this.form };
            if(this.mode === 'edit') {
                delete payload.username; // PK
                if(!payload.password) delete payload.password; // Don't send empty pass
                await this.$api.users.update(this.form.username, payload).execute();
            } else {
                await this.$api.users.create().execute(payload);
            }
            this.modalOpen = false;
            this.refresh();
        },
        async deleteUser(u) {
            if(confirm('Delete user?')) { await this.$api.users.delete(u).execute(); this.refresh(); }
        }
    }));

    // ------------------------------------------------------------------
    // MEDIA MANAGER (Drag & Drop)
    // ------------------------------------------------------------------
    Alpine.data('mediaManager', () => ({
        files: [],
        uploading: false,
        
        async init() { this.refresh(); },
        async refresh() { this.files = await this.$api.media.list().execute(); },
        
        async handleUpload(e) {
            const files = e.target.files || e.dataTransfer.files;
            if(!files.length) return;
            this.uploading = true;
            try { await this.$api.media.upload().execute(files); this.refresh(); }
            catch(e) { alert("Upload Failed"); }
            finally { this.uploading = false; }
        },
        async deleteFile(f) {
            if(confirm("Delete " + f + "?")) { await this.$api.media.delete(f).execute(); this.refresh(); }
        },
        copyUrl(url) { navigator.clipboard.writeText(url); }
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
                await this.refresh();

            } catch (e) {
                alert("Failed to save configuration: " + e.message);
            } finally {
                this.isSaving = false;
            }
        }
    }));
});