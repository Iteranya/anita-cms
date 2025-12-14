export default () =>  ({
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
    });
