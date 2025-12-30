export default () => ({
    files: [],
    metaMap: {},
    isLoading: false,

    // UI State
    activeTab: 'all',
    uploadModalOpen: false,
    detailsModalOpen: false,

    // Details Form
    targetFilename: '',
    targetId: null,
    form: { title: '', description: '', link: '' },

    // Upload Form
    uploadFile: null,
    uploadMeta: { title: '', description: '' },
    isUploading: false,

    async init() {
        await this.ensureSchema();
        await this.refresh();
    },

    // --- HELPER: Slugify Function ---
    slugify(text) {
        if (!text) return '';
        return text
            .toString()
            .toLowerCase()
            .trim()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-');        // Replace multiple - with single -
    },

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
                    tags: ["editor:create", "editor:read", "editor:delete", "editor:update"],
                    schema: {
                        fields: [
                            { name: "slug", label: "Slug", type: "text" },
                            { name: "saved_filename", label: "Filename", type: "text" },
                            { name: "friendly_name", label: "Title", type: "text" },
                            { name: "description", label: "Desc", type: "textarea" },
                            { name: "public_link", label: "Link", type: "text" }
                        ]
                    }
                };
                await this.$api.collections.create(payload).execute();
            }
        }
    },

    async refresh() {
        this.isLoading = true;
        try {
            const filesReq = await this.$api.media.list().execute();
            let metaList = [];
            try {
                metaList = await this.$api.collections.listRecords('media-data').execute();
            } catch (e) { }

            this.metaMap = {};
            metaList.forEach(item => {
                if (item.data && item.data.saved_filename) {
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
            title: filename,
            desc: 'Unregistered'
        };
    },

    openUpload() {
        this.uploadFile = null;
        this.uploadMeta = { title: '', description: '' };
        this.uploadModalOpen = true;
        const input = document.getElementById('mm-file-input');
        if (input) input.value = '';
    },

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.uploadFile = file;
            if (!this.uploadMeta.title) {
                this.uploadMeta.title = file.name.split('.')[0];
            }
        }
    },

    async doUpload() {
        if (!this.uploadFile) return;
        this.isUploading = true;

        try {
            const res = await this.$api.media.upload().execute([this.uploadFile]);
            const savedFile = res.files[0];
            
            // FIX: Ensure unique slug by appending timestamp, as titles might duplicate
            const baseSlug = this.slugify(this.uploadMeta.title);
            const uniqueSlug = `${baseSlug}-${Date.now()}`; 

            const payload = {
                data: {
                    slug: uniqueSlug, // Using the helper
                    saved_filename: savedFile.saved_as,
                    friendly_name: this.uploadMeta.title,
                    description: this.uploadMeta.description,
                    public_link: '/media/' + savedFile.saved_as
                }
            };

            await this.$api.collections.createRecord('media-data', payload).execute();

            this.uploadModalOpen = false;
            this.refresh();

        } catch (e) {
            Alpine.store('notifications').error('Upload Failed', e);
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
        const baseSlug = this.slugify(this.form.title);
        
        // Optional: Keep original slug ID if editing, or create new unique one
        const uniqueSlug = this.targetId 
            ? baseSlug // If editing, we might want to keep it simple or append ID?
            : `${baseSlug}-${Date.now()}`;

        const payload = {
            data: {
                slug: uniqueSlug,
                saved_filename: this.targetFilename,
                friendly_name: this.form.title,
                description: this.form.description,
                public_link: '/media/' + this.targetFilename
            }
        };

        try {
            if (this.targetId) {
                await this.$api.collections.updateRecord('media-data', this.targetId, payload).execute();
            } else {
                await this.$api.collections.createRecord('media-data', payload).execute();
            }
            this.detailsModalOpen = false;
            this.refresh();
        } catch (e) {
            Alpine.store('notifications').error('Error Saving Metadata', e);
        }
    },

    async deleteMedia() {
        if (!confirm("Permanently delete this file?")) return;

        try {
            await this.$api.media.delete(this.targetFilename).execute();

            if (this.targetId) {
                await this.$api.collections.deleteRecord('media-data', this.targetId).execute();
            }

            this.detailsModalOpen = false;
            this.refresh();
        } catch (e) {
            Alpine.store('notifications').error('Error Deleting File', e);
        }
    },

    copyLink() {
        navigator.clipboard.writeText(this.form.link);
    }
});