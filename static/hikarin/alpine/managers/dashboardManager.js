/**
 * Alpine.js manager for the main dashboard.
 * Features a tabbed interface for Welcome, Stats, and Profile Settings.
 */
export default () => ({
    // --- State ---
    isLoading: true,
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
        settings: {},
        custom: {}
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
        this.$watch('user.settings.dark_mode', (isDark) => {
            if (isDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        });

        await this.refresh();
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

            // After fetching, populate the profile form with user data
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
        this.profileForm.display_name = this.user.display_name || '';
        this.profileForm.pfp_url = this.user.pfp_url || '';
        this.profileForm.settings.dark_mode = this.user.settings?.dark_mode || false;
        this.profileForm.custom.about_me = this.user.custom?.about_me || '';
        this.pfpPreviewUrl = null; 
    },

    async saveProfile() {
        // Construct the full payload including the new fields
        const payload = {
            display_name: this.profileForm.display_name,
            pfp_url: this.profileForm.pfp_url,
            settings: this.profileForm.settings,
            custom: this.profileForm.custom
        };
        
        try {
            const updatedUser = await this.$api.dashboard.updateMe().execute(payload);
            
            this.user = updatedUser; // Update main user object
            this.populateProfileForm(); // Re-sync form state
            
            Alpine.store('notifications').success('Profile Updated', 'Your changes have been saved.');
        } catch(e) {
            console.error("Profile update failed:", e);
            Alpine.store('notifications').error('Update Failed', e.message || 'Could not save profile.');
        }
    },

    async handlePfpSelection(event) {
        const file = event.target.files[0];
        if (!file) return;

        // 1. Client-Side Validation
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

        // 2. Generate Instant Preview
        // Revoke the old preview URL if it exists to prevent memory leaks
        if (this.pfpPreviewUrl) {
            URL.revokeObjectURL(this.pfpPreviewUrl);
        }
        this.pfpPreviewUrl = URL.createObjectURL(file);

        // 3. Trigger the actual upload
        this.uploadProfilePicture(file);
    },

    /**
     * Performs the API call to upload the file.
     * @param {File} file The validated file object to upload.
     */
    async uploadProfilePicture(file) {
        this.isUploadingPfp = true;
        try {
            const res = await this.$api.media.upload().execute([file]);
            
            if (res.files && res.files.length > 0) {
                // On success, update the form's URL with the permanent one
                this.profileForm.pfp_url = '/media/' + res.files[0].saved_as;
                // The preview will now be replaced by the official URL if the user saves
            } else {
                 throw new Error("Upload response did not contain file data.");
            }
        } catch (err) {
            Alpine.store('notifications').error('Upload Failed', err.message || 'The image could not be uploaded.');
            // On failure, clear the preview so the user isn't confused
            this.pfpPreviewUrl = null;
        } finally {
            this.isUploadingPfp = false;
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