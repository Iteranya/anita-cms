/**
 * Alpine.js manager for the main dashboard.
 * Features a tabbed interface for Welcome, Stats, and Profile Settings.
 */
export default () => ({
    // --- State ---
    isLoading: true,
    isLoggingOut: false,
    activeTab: 'welcome', // 'welcome' | 'stats' | 'settings'

    stats: {
        core_counts: { pages: 0, forms: 0, submissions: 0, users: 0, tags: 0 },
        page_stats: { public_count: 0, blog_posts_count: 0 },
        activity: { top_forms_by_submission: [], top_tags_on_pages: [] },
        recent_items: { newest_pages: [], latest_updates: [], latest_submissions: [] }
    },
    user: {
        username: '',
        display_name: '',
        pfp_url: '',
        role: '',
        // Initialize with expected structure to be safe
        settings: { dark_mode: false },
        custom: { about_me: '' }
    },
    
    // --- Profile Edit Form State ---
    profileForm: {
        display_name: '',
        pfp_url: '',
        settings: {
            dark_mode: false
        },
        custom: {
            about_me: ''
        }
    },

    isUploadingPfp: false,
    pfpPreviewUrl: null,

    // --- Lifecycle & Data Fetching ---

    async init() {
        // Watch for changes to the user's dark mode setting and apply it globally.
        await this.ensureFileSchema()
        await this.ensureMediaSchema()
        this.$watch('user.settings.dark_mode', (isDark) => {
            if (isDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        });


        await this.refresh();
    },

    async ensureMediaSchema() {
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
                            {name: "slug", label: "Slug", type: "text"},
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

    async ensureFileSchema() {
            try {
                await this.$api.collections.get('file-data').execute();
            } catch (e) {
                if (e.status === 404) {
                    const payload = {
                        slug: "file-data",
                        title: "File Registry",
                        description: "Registry for documents and generic files",
                        tags: ["editor:create","editor:read", "editor:delete", "editor:update"],
                        schema: { fields: [
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
            const [statsData, userData] = await Promise.all([
                this.$api.dashboard.stats().execute(),
                this.$api.dashboard.me().execute()
            ]);

            this.stats = statsData;
            this.user = userData;

            // --- FIX: Normalize user data to prevent errors ---
            // This ensures nested objects exist and have default values. It prevents
            // errors if a new user has `null` or an empty object `{}` for these fields.
            // The spread syntax safely handles if `this.user.settings` is null or undefined.
            this.user.settings = { dark_mode: false, ...this.user.settings };
            this.user.custom = { about_me: '', ...this.user.custom };
            // --- END FIX ---

            // After fetching and normalizing, populate the profile form
            this.populateProfileForm();

        } catch (e) {
            console.error("Failed to load dashboard data:", e);
            Alpine.store('notifications').error("Load Failed", "Could not fetch dashboard data.");
        } finally {
            this.isLoading = false;
        }
    },

    // --- Profile Form Logic ---

     populateProfileForm() {
        // This code is now safer because we know user.custom and user.settings exist
        this.profileForm.display_name = this.user.display_name || '';
        this.profileForm.pfp_url = this.user.pfp_url || '';
        this.profileForm.settings.dark_mode = this.user.settings.dark_mode || false;
        this.profileForm.custom.about_me = this.user.custom.about_me || '';
        this.pfpPreviewUrl = null; 
    },

    async saveProfile() {
        const payload = {
            display_name: this.profileForm.display_name,
            pfp_url: this.profileForm.pfp_url,
            settings: this.profileForm.settings,
            custom: this.profileForm.custom
        };
        
        try {
            const updatedUser = await this.$api.dashboard.updateMe().execute(payload);
            
            // The API response should also be normalized just in case
            this.user = updatedUser;
            this.user.settings = { dark_mode: false, ...this.user.settings };
            this.user.custom = { about_me: '', ...this.user.custom };

            this.populateProfileForm();
            
            Alpine.store('notifications').success('Profile Updated', 'Your changes have been saved.');
        } catch(e) {
            console.error("Profile update failed:", e);
            Alpine.store('notifications').error('Update Failed', e.message || 'Could not save profile.');
        }
    },

    async handlePfpSelection(event) {
        const file = event.target.files[0];
        if (!file) return;

        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            Alpine.store('notifications').error('Invalid File Type', 'Please select a JPG, PNG, GIF, or WEBP image.');
            return;
        }

        const maxSizeInMB = 2;
        if (file.size > maxSizeInMB * 1024 * 1024) {
            Alpine.store('notifications').error('File Too Large', `Image size cannot exceed ${maxSizeInMB}MB.`);
            return;
        }

        if (this.pfpPreviewUrl) {
            URL.revokeObjectURL(this.pfpPreviewUrl);
        }
        this.pfpPreviewUrl = URL.createObjectURL(file);

        this.uploadProfilePicture(file);
    },

    async uploadProfilePicture(file) {
        this.isUploadingPfp = true;
        try {
            const res = await this.$api.media.upload().execute([file]);
            
            if (res.files && res.files.length > 0) {
                this.profileForm.pfp_url = '/media/' + res.files[0].saved_as;
            } else {
                 throw new Error("Upload response did not contain file data.");
            }
        } catch (err) {
            Alpine.store('notifications').error('Upload Failed', err.message || 'The image could not be uploaded.');
            this.pfpPreviewUrl = null;
        } finally {
            this.isUploadingPfp = false;
        }
    },

    async logout() {
        this.isLoggingOut = true;
        try {
            await this.$api.dashboard.logout().execute();
            window.location.href = '/auth/login'; 
        } catch (e) {
            console.error("Logout failed:", e);
            Alpine.store('notifications').error('Logout Failed', 'Could not log out. Please try again.');
        } finally {
            this.isLoggingOut = false;
        }
    },

    // --- Helpers ---

    get welcomeMessage() {
        return `Welcome, ${this.user.display_name || this.user.username}!`;
    },

    formatDate(isoString) {
        if (!isoString) return 'N/A';
        return new Date(isoString).toLocaleString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    },
});