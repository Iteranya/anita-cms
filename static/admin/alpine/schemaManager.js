export default () => ({
    collections: [],
    modalOpen: false,
    mode: 'create',
    
    def: {
        title: '', 
        slug: '', 
        description: '', 
        labels: [], 
        schemaString: '{\n  "type": "object",\n  "properties": {\n    "field_name": {"type": "string"}\n  }\n}'
    },
    targetSlug: '',
    labelInput: '',

    async init() { await this.refresh(); },
    
    async refresh() {
        const req = await this.$api.collections.list().execute();
        this.collections = req;
    },

    openCreate() {
        this.def = { title: '', slug: '', description: '', labels: [], schemaString: '{\n  "type": "object",\n  "properties": {\n    "field_name": {"type": "string"}\n  }\n}' };
        this.mode = 'create';
        this.modalOpen = true;
    },

    openEdit(item) {
        this.mode = 'edit';
        this.targetSlug = item.slug;
        this.def.title = item.title;
        this.def.slug = item.slug;
        this.def.description = item.description;
        this.def.labels = item.labels ? [...item.labels] : [];
        this.def.schemaString = JSON.stringify(item.schema || {}, null, 2);
        this.modalOpen = true;
    },

    generateSlug() {
        if(this.mode === 'create') this.def.slug = this.def.title.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
    },

    addLabel() { if(this.labelInput) this.def.labels.push(this.labelInput); this.labelInput = ''; },
    removeLabel(i) { this.def.labels.splice(i, 1); },

    async save() {
        let parsedSchema;
        try { parsedSchema = JSON.parse(this.def.schemaString); } catch(e) { alert("Invalid JSON Schema"); return; }
        
        const payload = {
            title: this.def.title,
            slug: this.def.slug,
            description: this.def.description,
            labels: this.def.labels,
            schema: parsedSchema,
            custom: {}
        };

        try {
            if(this.mode === 'create') await this.$api.collections.create().execute(payload);
            else await this.$api.collections.update().execute(this.targetSlug, payload);
            this.modalOpen = false;
            this.refresh();
            Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
        } catch(e) { Alpine.store('notifications').error('Create Form Failed', e); }
    },
    
    async deleteCollection(slug) {
        if(!confirm("Delete this entire collection and all its data?")) return;
        await this.$api.collections.delete(slug).execute();
        this.refresh();
    }
});