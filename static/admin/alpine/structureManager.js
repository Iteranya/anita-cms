export default () => ({
    pages: [], 
    roles: [], 
    isLoading: false,
    rolesPromise: null,

    // UI State
    pageTree: {}, 
    openGroups: [], // Tracks which folders are expanded (for the new UI)
    isCreatingGroup: false,
    newGroupName: '',
    
    // Modal State
    activeTab: 'general', 
    modalOpen: false,
    deleteModalOpen: false,
    isSaving: false,
    mode: 'create', 
    targetSlug: '',

    // Collection Data
    collection: {
        title: '',
        slug: '',
        content: '', 
        type: 'markdown', 
        thumb: '',
        tags:[],
        category: '', 
        isPublic: false, 
        isHome: false,   
        isTemplate:false,
        permissions: {} 
    },

    async init() {
        // Initialize with all groups open by default (optional)
        this.openGroups = ['uncategorized']; 
        await Promise.all([
            this.refresh(),
            this.fetchRoles()
        ]);
    },

    async refresh() {
        this.isLoading = true;
        this.rolesPromise = this.fetchRoles(); 
        try {
            this.pages = await this.$api.pages.list().execute();
            this.buildPageTree();
        } catch(e) {
            console.error(e);
            Alpine.store('notifications').error("Load Error", "Failed to load page list.");
        } finally {
            this.isLoading = false;
        }
    },

    async fetchRoles() {
        try {
            const names = await this.$api.users.role_name().execute();
            this.roles = names || [];
        } catch (e) {
            console.error("Failed to load roles", e);
        }
    },

    buildPageTree() {
        // 1. Identify all current keys to preserve them
        const currentKeys = Object.keys(this.pageTree);
        const tree = { uncategorized: [] };

        // 2. Preserve empty user-created groups
        currentKeys.forEach(key => {
            if(key !== 'uncategorized') tree[key] = [];
        });

        // 3. Distribute pages
        this.pages.forEach(page => {
            const mainLabel = (page.labels || []).find(t => t.startsWith('main:'));
            const groupName = mainLabel ? mainLabel.split(':')[1] : 'uncategorized';

            if (!tree[groupName]) {
                tree[groupName] = [];
            }
            tree[groupName].push(page);
        });
        
        // 4. Sort Keys
        const sortedKeys = Object.keys(tree).sort((a, b) => {
            if (a === 'uncategorized') return -1;
            if (b === 'uncategorized') return 1;
            return a.localeCompare(b);
        });

        const sortedTree = {};
        sortedKeys.forEach(key => {
            sortedTree[key] = tree[key];
            // Auto-open groups that have content if not already tracked
            if(!this.openGroups.includes(key) && tree[key].length > 0) {
                this.openGroups.push(key);
            }
        });

        this.pageTree = sortedTree;
    },

    toggleGroup(groupName) {
        if (this.openGroups.includes(groupName)) {
            this.openGroups = this.openGroups.filter(g => g !== groupName);
        } else {
            this.openGroups.push(groupName);
        }
    },

    /**
     * FIXED: Handle Drop Event
     */
    async handlePageDrop(itemSlug, position, newCategoryName) {
        // 1. LOCATE & REMOVE from Old Category (Optimistic update)
        let movedPage = null;
        
        // Find which category holds this page currently
        Object.keys(this.pageTree).forEach(cat => {
            const index = this.pageTree[cat].findIndex(p => p.slug === itemSlug);
            if (index !== -1) {
                // Remove from array and save reference
                movedPage = this.pageTree[cat].splice(index, 1)[0];
            }
        });

        if (!movedPage) return; // Should not happen

        // 2. INSERT into New Category (Optimistic update)
        // Ensure destination array exists
        if (!this.pageTree[newCategoryName]) {
            this.pageTree[newCategoryName] = [];
        }
        // Insert at specific index (position)
        this.pageTree[newCategoryName].splice(position, 0, movedPage);

        // 3. PREPARE API PAYLOAD
        // We reuse your existing logic to parse/compile labels
        // Reset collection just for calculation purposes
        this.collection = { permissions: this.getEmptyPermissions() }; 
        this.parseLabelsToCollection(movedPage.labels || []);
        
        // Update the category in the collection data
        this.collection.category = (newCategoryName === 'uncategorized') ? '' : newCategoryName;
        
        // Recompile labels
        const newLabels = this.compileLabelsFromCollection();
        const payload = { ...movedPage, labels: newLabels };

        // 4. SEND API REQUEST
        try {
            await this.$api.pages.update().execute(itemSlug, payload);
            Alpine.store('notifications').success('Page Moved', `Moved to ${newCategoryName}`);
            
            // Optional: Background refresh to ensure server consistency
            // We don't await this, so UI stays responsive
            this.refresh(); 
        } catch (e) {
            console.error("Failed to move page:", e);
            Alpine.store('notifications').error('Move Failed', 'Reverting changes...');
            
            // If failed, fully reload to revert the UI to server state
            await this.refresh();
        }
    },

    addNewGroup() {
        const cleanName = this.slugify(this.newGroupName);
        if (cleanName && !this.pageTree.hasOwnProperty(cleanName)) {
            this.pageTree[cleanName] = []; // Create empty array
            this.openGroups.push(cleanName); // Auto open
        }
        this.newGroupName = '';
        this.isCreatingGroup = false;
    },

    // --- Permission & Label Logic (Unchanged) ---
    getEmptyPermissions() {
        const perms = {};
        this.roles.forEach(role => {
            perms[role] = { create: false, read: false, update: false, delete: false };
        });
        return perms;
    },

    parseLabelsToCollection(labels = []) {
        this.collection.category = '';
        this.collection.isPublic = false;
        this.collection.isHome = false;
        this.collection.isTemplate = false;
        this.collection.isHead = false;
        this.collection.permissions = this.getEmptyPermissions();

        labels.forEach(label => {
            if (label === 'any:read') { this.collection.isPublic = true; return; }
            if (label === 'sys:home') { this.collection.isHome = true; return; }
            if (label === 'sys:template') {this.collection.isTemplate = true; return;}
            if (label === 'sys:head') {this.collection.isHead = true; return;}
            if (label.startsWith('main:')) { this.collection.category = label.split(':')[1]; return; }

            const parts = label.split(':');
            if (parts.length === 2) {
                const [role, action] = parts;
                if (this.collection.permissions[role]) this.collection.permissions[role][action] = true;
            }
        });
    },

    compileLabelsFromCollection() {
        const labels = [];
        if (this.collection.category) {
            const cleanCat = this.slugify(this.collection.category);
            labels.push(`main:${cleanCat}`);
        }
        if (this.collection.isPublic) labels.push('any:read');
        if (this.collection.isHome) labels.push('sys:home');
        if (this.collection.isTemplate) labels.push('sys:template');
        if (this.collection.isHead) labels.push('sys:head');

        Object.entries(this.collection.permissions).forEach(([role, actions]) => {
            Object.entries(actions).forEach(([action, isEnabled]) => {
                if (isEnabled) labels.push(`${role}:${action}`);
            });
        });
        return labels;
    },

    // --- Collection Handling ---
    async openCreate() {
        if (this.rolesPromise) await this.rolesPromise;
        this.mode = 'create';
        this.activeTab = 'general';
        this.collection = {
            title: '', slug: '', content: '', type: 'markdown', thumb: '',
            category: '', isPublic: false, isHome: false, isTemplate: false,
            permissions: this.getEmptyPermissions()
        };
        this.modalOpen = true;
    },

    async openEdit(page) {
        if (this.rolesPromise) await this.rolesPromise;
        this.mode = 'edit';
        this.targetSlug = page.slug;
        this.activeTab = 'general';
        this.collection.title = page.title;
        this.collection.slug = page.slug;
        this.collection.type = page.type || 'markdown';
        this.collection.thumb = page.thumb || '';
        this.collection.content = page.content || '';
        this.collection.tags = page.tags || [];
        this.parseLabelsToCollection(page.labels || []);
        this.modalOpen = true;
    },

    handleTitleInput() {
        if (this.mode === 'create') this.collection.slug = this.slugify(this.collection.title);
    },
    handleCategoryInput() {
        this.collection.category = this.slugify(this.collection.category);
    },
    slugify(text) {
        return text.toLowerCase().trim().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
    },

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
                Alpine.store('notifications').error('Upload Failed', err);
            }
        }
    },

    async save() {
        this.isSaving = true;
        this.collection.slug = this.slugify(this.collection.slug);
        if(this.collection.category) this.collection.category = this.slugify(this.collection.category);

        const payload = {
            title: this.collection.title, 
            slug: this.collection.slug, 
            type: this.collection.type,
            thumb: this.collection.thumb, 
            content: this.collection.content,
            tags:this.collection.tags,
            labels: this.compileLabelsFromCollection(), 
            custom: {}
        };

        try {
            if(this.mode === 'create') {
                await this.$api.pages.create().execute(payload);
            } else {
                await this.$api.pages.update().execute(this.targetSlug, payload);
            }
            this.modalOpen = false;
            Alpine.store('notifications').success('Saved', 'Page saved successfully.');
            await this.refresh(); 
        } catch(e) {
            console.error(e);
            Alpine.store('notifications').error('Save Failed', e);
        } finally {
            this.isSaving = false;
        }
    },

    confirmDelete(slug) {
        this.targetSlug = slug;
        this.deleteModalOpen = true;
    },

    async doDelete() {
        try {
            await this.$api.pages.delete().execute(this.targetSlug);
            this.deleteModalOpen = false;
            Alpine.store('notifications').success('Deleted', 'Page removed.');
            await this.refresh(); 
        } catch(e) {
            Alpine.store('notifications').error('Delete Failed', e);
        }
    }
});