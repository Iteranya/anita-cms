export default () => ({
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
                        labels: ["editor:create","editor:read", "editor:delete", "editor:update"],
                        schema: { fields: [
                            {name: "slug", label: "Slug", type: "text"},
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
    });