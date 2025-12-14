export default () =>  ({
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
    });