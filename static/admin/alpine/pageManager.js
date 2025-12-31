export default () =>  ({
        pages: [],
        search: '',
        isLoading: false,
        
        // Modal State
        modalOpen: false,
        deleteModalOpen: false,
        mode: 'create', // 'create' | 'edit'
        targetSlug: '',

        // Collection Data
        collection: {
            title: '',
            slug: '',
            description: '',
            thumb: '',
            type: 'markdown', // markdown | html
            labelInput: '',
            labels: [],
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

        // --- Collection Logic ---

        openCreate() {
            this.mode = 'create';
            this.resetCollection();
            this.modalOpen = true;
        },

        openEdit(page) {
            this.mode = 'edit';
            this.targetSlug = page.slug;
            
            // Map API data to Collection
            this.collection.title = page.title;
            this.collection.slug = page.slug;
            this.collection.type = page.type || 'markdown';
            this.collection.thumb = page.thumb || '';
            this.collection.description = page.description || (page.custom ? page.custom.description : '') || '';
            this.collection.labels = page.labels ? [...page.labels] : [];
            
            // Handle Custom Fields (Convert Object -> Array)
            this.collection.customFields = [];
            if (page.custom) {
                Object.entries(page.custom).forEach(([k, v]) => {
                    if(k !== 'description') this.collection.customFields.push({k, v});
                });
            }
            
            this.modalOpen = true;
        },

        resetCollection() {
            this.collection = {
                title: '', slug: '', description: '', thumb: '',
                type: 'markdown', labelInput: '', labels: [], customFields: []
            };
        },

        generateSlug() {
            if (this.mode === 'create') {
                this.collection.slug = this.collection.title.toLowerCase()
                    .replace(/[^\w\s-]/g, '')
                    .replace(/\s+/g, '-');
            }
        },

        // --- Label & Field Logic ---

        addLabel() {
            const val = this.collection.labelInput.trim();
            if (val && !this.collection.labels.includes(val)) {
                this.collection.labels.push(val);
            }
            this.collection.labelInput = '';
        },
        removeLabel(index) { this.collection.labels.splice(index, 1); },

        addCustomField() { this.collection.customFields.push({k: '', v: ''}); },
        removeCustomField(index) { this.collection.customFields.splice(index, 1); },

        // --- Actions ---

        async uploadThumbnail(e) {
            const files = e.target.files;
            if(files.length > 0) {
                try {
                    const req = this.$api.media.upload();
                    const res = await req.execute(files);
                    if(res.files && res.files.length > 0) {
                        this.collection.thumb = '/media/' + res.files[0].saved_as;
                    }
                } catch(err) { 
                    Alpine.store('notifications').error('Upload Failed', err); ; 
                }
            }
        },

async save() {
            // 1. Prepare Metadata
            const customObj = { description: this.collection.description };
            this.collection.customFields.forEach(f => { if(f.k) customObj[f.k] = f.v; });

            // 2. Construct Payload
            const payload = {
                title: this.collection.title,
                slug: this.collection.slug,
                type: this.collection.type,
                thumb: this.collection.thumb,
                labels: this.collection.labels,
                custom: customObj
            };

            // Debug: Check console to ensure this object is not empty
            console.log("Submitting Payload:", payload);

            try {
                if(this.mode === 'create') {
                    await this.$api.pages.create().execute(payload);
                } else {
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
    });