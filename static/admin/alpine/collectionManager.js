export default () => ({
    collections: [],
    isLoading: false,
    activeTab: 'settings', // settings | builder | submissions
    role_name: [], // This will be populated on init

    // Modal State
    modalOpen: false,
    mode: 'create',
    currentSlug: '',

    // Collection Structure
    collection: {
        title: '',
        slug: '',
        description: '',
        fields: [], // Flat array for easier Alpine editing
        permissions: { // NEW: Replaces labels
            any: { create: false, read: false, update: false, delete: false },
            roles: {} // e.g. { admin: { create: true, ... } }
        }
    },

    // Submissions Data
    submissions: [],
    subsLoading: false,

    async init() {
        // Fetch the main collections list
        await this.refresh();

        // Now, fetch the role names using the new endpoint
        try {
            const names = await this.$api.users.role_name().execute();
            this.role_name = names || []; // Ensure it's an array even if the response is null
        } catch (e) {
            console.error("Failed to load role names:", e);
            // Optional: show a user-facing error
            Alpine.store('notifications').error('Error', 'Could not load user roles.');
        }
    },

    async refresh() {
        this.isLoading = true;
        try {
            this.collections = await this.$api.collections.list().execute();
        } catch (e) { console.error(e); }
        this.isLoading = false;
    },

    // --- Slug Logic ---
    handleTitleInput() {
        if (this.mode === 'create') {
            this.collection.slug = this.collection.title
                .toLowerCase()
                .trim()
                .replace(/\s+/g, '_')           // Spaces to underscores
                .replace(/[^\w]/g, '');         // Remove non-word chars
        }
    },

    sanitizeSlug() {
        this.collection.slug = this.collection.slug
            .toLowerCase()
            .replace(/\s+/g, '_')
            .replace(/[^\w]/g, '');
    },

    // --- Field Builder ---
    addField() {
        this.collection.fields.push({
            name: '',
            label: '',
            type: 'text',
            required: false
        });
    },

    removeField(index) {
        this.collection.fields.splice(index, 1);
    },

    updateFieldSlug(index) {
        // Auto-gen field name from label if name is empty
        if (!this.collection.fields[index].name) {
            this.collection.fields[index].name = this.collection.fields[index].label
                .toLowerCase()
                .replace(/\s+/g, '_')
                .replace(/[^\w]/g, '');
        }
    },

    // --- Permission Helpers ---
    getEmptyPermissions() {
        const perms = {
            any: { create: false, read: false, update: false, delete: false },
            roles: {}
        };
        this.role_name.forEach(role => {
            perms.roles[role] = { create: false, read: false, update: false, delete: false };
        });
        return perms;
    },

    parsePermissionsFromLabels(labels = []) {
        const perms = this.getEmptyPermissions();
        labels.forEach(label => {
            const parts = label.split(':');
            if (parts.length === 2) {
                const [entity, action] = parts;
                if (entity === 'any' && perms.any.hasOwnProperty(action)) {
                    // Handle 'any:read'
                    perms.any[action] = true;
                } else if (perms.roles.hasOwnProperty(entity) && perms.roles[entity].hasOwnProperty(action)) {
                    // Handle 'editor:read' by checking if the entity is a known role
                    perms.roles[entity][action] = true;
                }
            }
        });
        return perms;
    },

    formatPermissionsToLabels() {
        const labels = [];
        // Handle 'any' permissions
        for (const action in this.collection.permissions.any) {
            if (this.collection.permissions.any[action]) {
                labels.push(`any:${action}`);
            }
        }
        // Handle role-based permissions
        for (const role in this.collection.permissions.roles) {
            for (const action in this.collection.permissions.roles[role]) {
                if (this.collection.permissions.roles[role][action]) {
                    // CHANGE: Removed 'role:' prefix
                    labels.push(`${role}:${action}`);
                }
            }
        }
        return labels;
    },


    // --- Actions ---
    openCreate() {
        this.mode = 'create';
        this.activeTab = 'settings';
        this.collection = {
            title: '',
            slug: '',
            description: '',
            fields: [],
            permissions: this.getEmptyPermissions() // Initialize with roles
        };
        this.addField(); // Start with one field
        this.modalOpen = true;
    },

    async openEdit(item) {
        this.mode = 'edit';
        this.activeTab = 'settings';
        this.currentSlug = item.slug;

        this.collection = {
            title: item.title,
            slug: item.slug,
            description: item.description || '',
            permissions: this.parsePermissionsFromLabels(item.labels), // Parse labels into UI state
            fields: item.schema && item.schema.fields ? [...item.schema.fields] : []
        };
        this.modalOpen = true;
    },

    async save() {
        this.sanitizeSlug();
        const payload = {
            title: this.collection.title,
            slug: this.collection.slug,
            description: this.collection.description,
            labels: this.formatPermissionsToLabels(), // Convert permissions UI state back to labels
            schema: { fields: this.collection.fields },
            custom: {}
        };

        // Debug Payload
        console.log("Saving Collection:", payload);

        try {
            if (this.mode === 'create') {
                await this.$api.collections.create(payload).execute();
            } else {
                await this.$api.collections.update(this.currentSlug, payload).execute();
            }

            this.modalOpen = false;
            Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
            this.refresh();

        } catch (e) {
            console.error(e);
            Alpine.store('notifications').error('Could Not Save Collection', e);
        }
    },

    async deleteCollection(slug) {
        if (!confirm("Delete this collection and all data?")) return;
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