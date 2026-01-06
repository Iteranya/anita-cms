export default () =>  ({
        slug: '',
        collectionDef: null,
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
                Alpine.store('notifications').error('Missing Slug', 'No collection slug specified in URL.');
                return;
            }

            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                // A. Fetch Schema (to know columns/fields)
                this.collectionDef = await this.$api.collections.get(this.slug).execute();
                
                // Parse Schema for Table & Collection
                if(this.collectionDef.schema && this.collectionDef.schema.fields) {
                    this.fields = this.collectionDef.schema.fields;
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
    });