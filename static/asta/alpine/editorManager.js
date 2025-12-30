// asta/editorManager.js
export default (slug, initialData = {}) => ({
    slug: slug,
    editorInstance: null,
    
    // UI State
    isProcessing: false,
    statusText: 'Initializing...',
    
    // Data State
    content: '', // Current editor content
    currentPublicMarkdown: '', // The 'live' version (to avoid overwriting when drafting)
    currentCustom: {}, // To preserve other custom fields

    defaults: {
        markdown: '# New Page\nStart writing your content here...'
    },

    async init() {
        if (!window.AstaMilkdown) {
            console.error("AstaMilkdown not loaded");
            return;
        }

        await this.fetchAndInitEditor();
    },

    /**
     * Fetches data from API, determines whether to show Draft or Public content,
     * and initializes the editor.
     */
    async fetchAndInitEditor() {
        try {
            this.isProcessing = true;
            
            const response = await this.$api.asta.get(this.slug).execute();
            
            this.currentPublicMarkdown = response.markdown || '';
            this.currentCustom = response.custom || {};
            
            const draftContent = this.currentCustom.crepe;
            const startContent = draftContent || this.currentPublicMarkdown || this.defaults.markdown;

            this.content = startContent;

            // ------------------------------------------------------------------
            // ---  THE FIX IS HERE  ---
            // Before creating the editor, empty the target element.
            // This ensures that if init() runs again (e.g., due to HMR),
            // the old editor instance is removed from the DOM.
            if (this.$refs.editorRoot) {
                this.$refs.editorRoot.innerHTML = '';
            }
            // ------------------------------------------------------------------

            this.editorInstance = await window.AstaMilkdown.createEditor(this.$refs.editorRoot, {
                defaultValue: startContent,
                onUpdate: (md) => { 
                    this.content = md;
                    this.statusText = 'Unsaved changes';
                },
                uploadHandler: (file) => this.handleUpload(file)
            });

            this.statusText = 'Ready';

        } catch (error) {
            console.error("Init error:", error);
            this.statusText = 'Error loading data';
        } finally {
            this.isProcessing = false;
        }
    },

    /**
     * SYNC DRAFT
     * Saves to custom.crepe (hidden from public view).
     */
    async syncDraft() {
        this.isProcessing = true;
        this.statusText = 'Saving Draft...';

        try {
            const payload = {
                markdown: this.currentPublicMarkdown, 
                custom: {
                    ...this.currentCustom,
                    crepe: this.content
                }
            };

            await this.$api.asta.updateMarkdown().execute(this.slug, payload);
            
            this.currentCustom = payload.custom;
            
            this.statusText = 'Draft Saved';
            
            this.$store.notifications.add({
                type: 'success',
                title: 'Draft Saved',
                message: 'Content saved to custom.crepe'
            });

        } catch (e) {
            console.error("Sync error", e);
            this.statusText = 'Save Failed';
        } finally {
            this.isProcessing = false;
        }
    },

    /**
     * DEPLOY
     * Pushes content to the public 'markdown' field.
     */
    async deploy() {
        this.isProcessing = true;
        this.statusText = 'Deploying...';

        try {
            const payload = {
                markdown: this.content,
                custom: {
                    ...this.currentCustom,
                    crepe: this.content
                }
            };

            await this.$api.asta.updateMarkdown().execute(this.slug, payload);

            this.currentPublicMarkdown = this.content;
            this.currentCustom = payload.custom;

            this.statusText = 'Deployed';
            this.$store.notifications.add({
                type: 'success',
                title: 'Published',
                message: 'Page is now live.'
            });

        } catch (error) {
            console.error("Deploy error:", error);
            this.$store.notifications.add({ type: 'error', message: 'Deployment failed.' });
            this.statusText = 'Error';
        } finally {
            this.isProcessing = false;
        }
    },

    /**
     * MODIFIED: UPLOAD LOGIC
     * Uses the centralized this.$api.asta.upload() method.
     */
    async handleUpload(file) {
        this.statusText = `Uploading ${file.name}...`;
        console.log(`[Upload] 🚀 Using AstaAPI for upload...`);

        try {
            // The API expects an array of files.
            const response = await this.$api.asta.upload().execute([file]);

            // --- FIX STARTS HERE ---

            // 1. Validate the main response object and the 'files' array.
            if (!response || !response.files || response.files.length === 0) {
                throw new Error("Invalid API response from upload endpoint.");
            }
            
            // 2. Get the report for the first (and only) file uploaded.
            const fileReport = response.files[0];

            // 3. Check for a file-specific error returned from the backend.
            if (fileReport.error) {
                throw new Error(`Server failed to process file '${fileReport.original}': ${fileReport.error}`);
            }

            // 4. Ensure the URL exists in the file report.
            if (!fileReport.url) {
                throw new Error("API response for file is missing a URL.");
            }
            
            const uploadedFileUrl = fileReport.url;
            console.log(`[Upload] ✅ SUCCESS:`, uploadedFileUrl);

            // --- FIX ENDS HERE ---
            
            this.statusText = 'Unsaved changes'; // Reset status after successful upload
            
            // Return the URL for the editor to display the image
            return uploadedFileUrl; 

        } catch (error) {
            console.error(`[Upload] 💥 API ERROR:`, error);
            this.statusText = 'Upload Error';
            this.$store.notifications.add({ 
                type: 'error', 
                message: `Upload failed: ${error.message || 'Check console.'}` 
            });
            // Re-throw the error so the editor's internal logic knows it failed.
            throw error;
        }
    },

    focusEditor(e) {
        const pm = this.$refs.editorRoot.querySelector('.ProseMirror');
        if (pm && (e.target === e.currentTarget || e.target === this.$refs.editorRoot)) {
            pm.focus();
        }
    }
});