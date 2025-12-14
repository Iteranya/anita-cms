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

        // Forms
        userForm: { username: '', display_name: '', role: 'viewer', disabled: false, password: '' },
        passwordForm: { username: '', new_password: '' },
        roleForm: { role_name: '', permissions: [] },
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
                name: 'Forms & Submissions',
                perms: [
                    { key: 'form:create', label: 'Create Forms', desc: 'Allows creating new forms, including defining fields, settings, and behavior.' },
{ key: 'form:read', label: 'View Forms', desc: 'Allows viewing existing forms and their configuration.' },
{ key: 'form:update', label: 'Edit Forms', desc: 'Allows editing or modifying existing forms and their settings.' },
{ key: 'form:delete', label: 'Delete Forms', desc: 'Allows deleting forms entirely from the system.' },

{ key: 'submission:create', label: 'Create Submissions (Override)', desc: 'Allows creating form submissions even when the form’s own access rules would normally prevent it.' },
{ key: 'submission:read', label: 'View Submissions (Override)', desc: 'Allows viewing any form submissions regardless of the form’s internal permission rules.' },
{ key: 'submission:update', label: 'Edit Submissions (Override)', desc: 'Allows editing any form submission even if role-based or form-level rules would normally block it.' },
{ key: 'submission:delete', label: 'Delete Submissions (Override)', desc: 'Allows deleting any form submission regardless of the form’s access restrictions.' },

                ]
            },
            {
                name: 'Media Library',
                perms: [
                    { key: 'media:create', label: 'Upload Media', desc: 'Allows uploading new media files into the media library.' },
{ key: 'media:read', label: 'View Media Library', desc: 'Allows browsing and viewing items in the media library.' },
{ key: 'media:update', label: 'Edit Media Metadata', desc: 'Allows editing media details such as titles, descriptions, and tags.' },
{ key: 'media:delete', label: 'Delete Media', desc: 'Allows permanently deleting media files from the library.' },

                ]
            },
            {
                name: 'Blog System',
                perms: [
                  { key: 'blog:create', label: 'Create Posts', desc: 'Allows writing and publishing new blog posts.' },
{ key: 'blog:read', label: 'Read Posts', desc: 'Allows access to view all blog posts in the system.' },
{ key: 'blog:update', label: 'Edit Posts', desc: 'Allows modifying existing blog posts.' },
{ key: 'blog:delete', label: 'Delete Posts', desc: 'Allows deleting blog posts permanently.' },

                ]
            },
            {
                name: 'Pages & Content',
                perms: [
                    { key: 'page:create', label: 'Create Pages', desc: 'Allows creating new pages in the CMS.' },
{ key: 'page:read', label: 'View Pages', desc: 'Allows viewing all pages within the CMS.' },
{ key: 'page:update', label: 'Edit Pages', desc: 'Allows modifying page content, metadata, and settings.' },
{ key: 'page:delete', label: 'Delete Pages', desc: 'Allows deleting pages from the CMS.' },

                ]
            },
            {
                name: 'System & AI',
                perms: [
                  { key: 'config:read', label: 'View Config', desc: 'Allows viewing system configuration values without exposing sensitive secrets.' },
{ key: 'config:update', label: 'Edit Config', desc: 'Allows editing or updating system configuration values.' },

{ key: 'aina', label: 'Access Aina (HTML AI)', desc: 'Allows using Aina, the HTML-based AI assistant.' },
{ key: 'asta', label: 'Access Asta (Markdown AI)', desc: 'Allows using Asta, the Markdown Editor.' },

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
            this.userForm = { username: '', display_name: '', role: firstRole, disabled: false, password: '' };
            this.userModalOpen = true;
        },

        openEditUser(user) {
            this.isEditingUser = true;
            this.userForm = { 
                username: user.username,
                display_name: user.display_name,
                role: user.role,
                disabled: user.disabled,
                password: '' 
            };
            this.userModalOpen = true;
        },

        openPasswordModal(user) {
            this.passwordForm = { username: user.username, new_password: '' };
            this.passwordModalOpen = true;
        },

        async saveUser() {
            try {
                const payload = {
                    display_name: this.userForm.display_name,
                    role: this.userForm.role,
                    disabled: this.userForm.disabled
                };

                if (this.isEditingUser) {
                    await this.$api.users.update(this.userForm.username, payload).execute();
                } else {
                    payload.username = this.userForm.username;
                    payload.password = this.userForm.password;
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
                await this.$api.users.update(this.passwordForm.username, { 
                    password: this.passwordForm.new_password 
                }).execute();
                
                this.passwordModalOpen = false;
                alert('Password updated');
            } catch(e) { Alpine.store('notifications').error('Update Password Failed', e);  }
        },

        // --- ROLE LOGIC (Split Pane) ---

        selectRole(role) {
            this.selectedRole = role; // Reference for UI highlight
            this.roleForm = {
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
            if (this.roleForm.permissions.includes(key)) {
                this.roleForm.permissions = this.roleForm.permissions.filter(p => p !== key);
            } else {
                this.roleForm.permissions.push(key);
            }
        },

        async saveRole() {
            if(!this.selectedRole) return;
            try {
                const payload = {
                    role_name: this.roleForm.role_name,
                    permissions: this.roleForm.permissions
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