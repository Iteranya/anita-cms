export default () =>  ({
        view: 'users', // 'users' | 'roles'
        isLoading: false,
        
        // Data
        users: [],
        roles: [], // Array of objects
        // Selection State (for Roles Split Pane)
        selectedRole: null, 

        // Modals
        userModalOpen: false,
        passwordModalOpen: false,
        deleteModalOpen: false,
        isEditingUser: false,

        // Collections
        userCollection: { username: '', display_name: '', role: 'viewer', disabled: false, password: '' },
        passwordCollection: { username: '', new_password: '' },
        roleCollection: { role_name: '', permissions: [] },
        deleteTarget: { type: '', id: '' },

        // Static Data: Permission Categories
        permCategories: [
    {
        name: 'Administrator',
        perms: [
            { key: '*', label: 'Administrator', desc: 'Grants full unrestricted access to all system features, settings, content, and tools.' }
        ]
    },
    {
        name: 'Collections & Submissions',
        perms: [
            { key: 'collection:create', label: 'Create Collections', desc: 'Allows creating new collections, including defining fields, settings, and behavior.' },
            { key: 'collection:read', label: 'View Collections', desc: 'Allows viewing existing collections and their configuration.' },
            { key: 'collection:update', label: 'Edit Collections', desc: 'Allows editing or modifying existing collections and their settings.' },
            { key: 'collection:delete', label: 'Delete Collections', desc: 'Allows deleting collections entirely from the system.' },
            
            { key: 'submission:create', label: 'Create Submissions (Override)', desc: 'Allows creating collection submissions even when the collection’s own access rules would normally prevent it.' },
            { key: 'submission:read', label: 'View Submissions (Override)', desc: 'Allows viewing any collection submissions regardless of the collection’s internal permission rules.' },
            { key: 'submission:update', label: 'Edit Submissions (Override)', desc: 'Allows editing any collection submission even if role-based or collection-level rules would normally block it.' },
            { key: 'submission:delete', label: 'Delete Submissions (Override)', desc: 'Allows deleting any collection submission regardless of the collection’s access restrictions.' }
        ]
    },
    {
        name: 'Media Library',
        perms: [
            { key: 'media:create', label: 'Upload Media', desc: 'Allows uploading new media files into the media library.' },
            { key: 'media:read', label: 'View Media Library', desc: 'Allows browsing and viewing all items in the media library.' },
            { key: 'media:update', label: 'Edit Media Metadata', desc: 'Allows editing media details such as titles, descriptions, and labels.' },
            { key: 'media:delete', label: 'Delete Media', desc: 'Allows permanently deleting media files from the library.' }
        ]
    },
    {
        name: 'Pages & Content',
        perms: [
            { key: 'page:create', label: 'Create Pages (System)', desc: 'Allows creating new pages anywhere in the CMS.' },
            { key: 'page:read', label: 'View Pages (System)', desc: 'Allows viewing all pages within the CMS, overriding any page-specific restrictions.' },
            { key: 'page:update', label: 'Edit Pages (System)', desc: 'Allows modifying any page’s content, metadata, and settings.' },
            { key: 'page:delete', label: 'Delete Pages (System)', desc: 'Allows deleting any page from the CMS.' }
        ]
    },
    {
        name: 'System & AI Editors',
        perms: [
            { key: 'config:read', label: 'View System Config', desc: 'Allows viewing system configuration values without exposing sensitive secrets.' },
            { key: 'config:update', label: 'Edit System Config', desc: 'Allows editing or updating system configuration values.' },

            { key: 'html:create', label: 'Set Page Type to HTML', desc: 'Grants the ability to mark a page’s content type as HTML.' },
            { key: 'html:read', label: 'Access Aina (HTML Editor)', desc: 'Grants the ability to open and use the Aina HTML editor.' },
            { key: 'html:update', label: 'Save in Aina (HTML Editor)', desc: 'Grants the ability to save changes made within the Aina editor.' },
            { key: 'html:delete', label: 'Delete HTML Page Content', desc: 'Unused, I just like symmetry.' },

            { key: 'markdown:create', label: 'Set Page Type to Markdown', desc: 'Grants the ability to mark a page’s content type as Markdown.' },
            { key: 'markdown:read', label: 'Access Asta (Markdown Editor)', desc: 'Grants the ability to open and use the Asta Markdown editor.' },
            { key: 'markdown:update', label: 'Save in Asta (Markdown Editor)', desc: 'Grants the ability to save changes made within the Asta editor.' },
            { key: 'markdown:delete', label: 'Delete Markdown Page Content', desc: 'Unusued, I just like symmetry.' }
        ]
    }
],

        async init() {
            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                const [uReq, rReq] = await Promise.all([
                    this.$api.users.list().execute(),
                    this.$api.users.roles().execute()
                ]);
                
                this.users = uReq || [];
                
                // Handle Dictionary -> Array conversion for Roles
                if (rReq && !Array.isArray(rReq) && typeof rReq === 'object') {
                    this.roles = Object.entries(rReq).map(([k, v]) => ({ role_name: k, permissions: v }));
                } else {
                    this.roles = rReq || [];
                }

                // Reselect role if active to update permissions visual state
                if(this.selectedRole) {
                    const found = this.roles.find(r => r.role_name === this.selectedRole.role_name);
                    if(found) this.selectRole(found);
                }

            } catch(e) { console.error(e); }
            finally { this.isLoading = false; }
        },

        // --- USER LOGIC ---

        openCreateUser() {
            this.isEditingUser = false;
            const firstRole = this.roles.length > 0 ? this.roles[0].role_name : 'viewer';
            this.userCollection = { username: '', display_name: '', role: firstRole, disabled: false, password: '' };
            this.userModalOpen = true;
        },

        openEditUser(user) {
            this.isEditingUser = true;
            this.userCollection = { 
                username: user.username,
                display_name: user.display_name,
                role: user.role,
                disabled: user.disabled,
                password: '' 
            };
            this.userModalOpen = true;
        },

        openPasswordModal(user) {
            this.passwordCollection = { username: user.username, new_password: '' };
            this.passwordModalOpen = true;
        },

        async saveUser() {
            try {
                const payload = {
                    display_name: this.userCollection.display_name,
                    role: this.userCollection.role,
                    disabled: this.userCollection.disabled
                };

                if (this.isEditingUser) {
                    await this.$api.users.update(this.userCollection.username, payload).execute();
                } else {
                    payload.username = this.userCollection.username;
                    payload.password = this.userCollection.password;
                    await this.$api.users.create().execute(payload);
                }
                this.userModalOpen = false;
                this.refresh();
            } catch(e) { Alpine.store('notifications').error('Save Failed', e);  }
        },

        async changePassword() {
            // Assuming a custom endpoint or generic update
            try {
                // If your API has a specific endpoint, use that. 
                // Otherwise, some systems allow password update via standard PUT if permissions allow.
                // We'll try the standard update first.
                await this.$api.users.update(this.passwordCollection.username, { 
                    password: this.passwordCollection.new_password 
                }).execute();
                
                this.passwordModalOpen = false;
                alert('Password updated');
            } catch(e) { Alpine.store('notifications').error('Update Password Failed', e);  }
        },

        // --- ROLE LOGIC (Split Pane) ---

        selectRole(role) {
            this.selectedRole = role; // Reference for UI highlight
            this.roleCollection = {
                role_name: role.role_name,
                permissions: [...role.permissions] // Deep copy perms
            };
        },

        createNewRole() {
            const name = 'New Role ' + (this.roles.length + 1);
            const newRole = { role_name: name, permissions: [] };
            this.roles.push(newRole);
            this.selectRole(newRole);
        },

        togglePermission(key) {
            if (this.roleCollection.permissions.includes(key)) {
                this.roleCollection.permissions = this.roleCollection.permissions.filter(p => p !== key);
            } else {
                this.roleCollection.permissions.push(key);
            }
        },

        async saveRole() {
            if(!this.selectedRole) return;
            try {
                const payload = {
                    role_name: this.roleCollection.role_name,
                    permissions: this.roleCollection.permissions
                };
                
                // Using generic POST to /users/roles/
                await this.$api._request('POST', '/users/roles/', { body: payload });
                
                // Visual feedback
                const btn = document.getElementById('save-role-btn');
                const oldText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i> Saved';
                setTimeout(() => btn.innerHTML = oldText, 2000);

                this.refresh();
            } catch(e) { Alpine.store('notifications').error('Save Failed', e); }
        },

        // --- SHARED DELETE LOGIC ---

        confirmDelete(type, id) {
            this.deleteTarget = { type, id };
            this.deleteModalOpen = true;
        },

        async doDelete() {
            try {
                if (this.deleteTarget.type === 'user') {
                    await this.$api.users.delete(this.deleteTarget.id).execute();
                } else {
                    await this.$api._request('DELETE', `/users/roles/${this.deleteTarget.id}`);
                    // If we deleted the currently viewed role, deselect
                    if(this.selectedRole && this.selectedRole.role_name === this.deleteTarget.id) {
                        this.selectedRole = null;
                    }
                }
                this.deleteModalOpen = false;
                this.refresh();
            } catch(e) { Alpine.store('notifications').error('Delete Failed', e); }
        }
    });