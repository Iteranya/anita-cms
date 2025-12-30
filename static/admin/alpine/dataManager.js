export default () =>  ({
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
    });