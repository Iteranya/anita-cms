export default () =>  ({
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
                        tags: ["editor:create","editor:read", "editor:delete", "editor:update"],
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
                console.log(this.targetFilename) // Exists
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

        async batchUpload(e) {
            const files = Array.from(e.target.files || []);
            if (!files.length) return;

            this.isUploading = true;

            try {
                // Upload all files in one go
                await this.$api.media.upload().execute(files);

                // Reset input so same files can be re-selected later
                e.target.value = '';

                // Refresh media list
                await this.refresh();

            } catch (err) {
                Alpine.store('notifications').error('Batch Upload Failed', err);
            } finally {
                this.isUploading = false;
            }
        },

        copyLink() {
            navigator.clipboard.writeText(this.form.link);
            // Optional: visual feedback handled in UI via x-data local state
        }
    });