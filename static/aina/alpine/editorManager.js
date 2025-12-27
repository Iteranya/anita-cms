export default (slug, initialData = {}) => ({
    slug: slug,
    isProcessing: false,
    statusText: 'Ready',
    editors: { html: null, css: null },
    
    // Internal State
    currentHead: '', // Holds the raw HTML string for <head> from DB
    currentScript: '', // Holds the raw JS string from DB
    
    // Default Fallbacks (Only used if DB is empty)
    defaults: {
        html: `<div class="p-10">\n  <h1 class="text-3xl font-bold text-blue-600">New Page</h1>\n  <p>Start editing...</p>\n</div>`,
        css: `body { background-color: #f3f4f6; }`
    },

    async init() {
        // 1. Initialize HTML Editor
        this.editors.html = window.AceService.init(
            this.$refs.htmlEditor, 
            'html', 
            initialData.html || this.defaults.html
        );

        // 2. Initialize CSS Editor
        this.editors.css = window.AceService.init(
            this.$refs.cssEditor, 
            'css', 
            initialData.css || this.defaults.css
        );

        // 3. Initial Load & Render
        await this.fetchAndRender();
    },

    /**
     * CORE ACTION: Sync / Save Draft
     * 1. Fetches latest Head/Script (Source of Truth).
     * 2. Merges with current Editor HTML/CSS.
     * 3. Saves to 'custom.builder'.
     * 4. Updates Preview.
     */
    async syncAndRender() {
        this.isProcessing = true;
        this.statusText = 'Syncing...';

        const userHtml = this.editors.html.getValue();
        const userCss = this.editors.css.getValue();

        try {
            // 1. Fetch current state first (To get the latest Head/Script config)
            const currentData = await this.$api.aina.get(this.slug).execute();
            const builder = currentData.custom?.builder || {};
            
            this.currentHead = builder.header || '';
            this.currentScript = builder.script || '';

            // 2. Prepare Payload (Merge local edits with server config)
            const payload = {
                custom: {
                    builder: {
                        ...builder, // Keep existing keys
                        content: userHtml,
                        style: userCss,
                        // Explicitly ensuring these aren't overwritten by stale local state
                        header: this.currentHead, 
                        script: this.currentScript
                    }
                }
            };
            
            // 3. Save (Background)
            const savePromise = this.$api.aina.updateHTML().execute(this.slug, payload);

            // 4. Render Preview Immediately
            this.updatePreview(userHtml, userCss, this.currentHead, this.currentScript);
            
            await savePromise;
            this.statusText = 'Saved';
        } catch (e) {
            console.error("Sync error", e);
            this.statusText = 'Save Failed';
        } finally {
            this.isProcessing = false;
        }
    },

    /**
     * CORE ACTION: Deploy
     * Compiles the final HTML and saves it to the public `html` field.
     */
    async deployHtml() {
        this.isProcessing = true;
        this.statusText = 'Deploying...';

        try {
            // 1. Fetch latest config (Database as Source of Truth)
            const response = await this.$api.aina.get(this.slug).execute();
            const builder = response.custom?.builder || {};
            
            // 2. Get latest values
            const head = builder.header || '';
            const script = builder.script || '';
            const html = this.editors.html.getValue();
            const css = this.editors.css.getValue();

            // 3. Compile
            const fullCompiledHtml = this.compilePage(html, css, head, script);

            // 4. Update Public HTML
            const payload = {
                html: fullCompiledHtml
            };

            await this.$api.aina.updateHTML().execute(this.slug, payload);
            
            this.$store.notifications.add({
                type: 'success',
                title: 'Deployed',
                message: 'Live page updated successfully.'
            });
            this.statusText = 'Deployed';

        } catch (error) {
            console.error("Deploy error:", error);
            this.$store.notifications.add({ type: 'error', message: 'Deployment failed.' });
            this.statusText = 'Error';
        } finally {
            this.isProcessing = false;
        }
    },

    /**
     * Fetches data from DB and updates the UI
     */
    async fetchAndRender() {
        try {
            const response = await this.$api.aina.get(this.slug).execute();
            const builder = response.custom?.builder || {};
            
            // Update Local State
            this.currentHead = builder.header || '';
            this.currentScript = builder.script || '';
            
            // Update Editors (Only if not already dirty? For now, we overwrite on load)
            // Note: In a real app, you might check if editors have unsaved changes before overwriting
            if (builder.content) this.editors.html.setValue(builder.content, -1);
            if (builder.style) this.editors.css.setValue(builder.style, -1);

            // Render Iframe
            this.updatePreview(
                this.editors.html.getValue(), 
                this.editors.css.getValue(), 
                this.currentHead, 
                this.currentScript
            );

        } catch (error) {
            console.error("Fetch render error:", error);
        }
    },

    /**
     * Updates the iframe srcdoc
     */
    updatePreview(html, css, head, script) {
        if (this.$refs.previewFrame) {
            this.$refs.previewFrame.srcdoc = this.compilePage(html, css, head, script);
        }
    },

    /**
     * The Compiler
     */
    compilePage(htmlContent, cssContent, headContent, jsContent) {
        // Check if Tailwind is present in the head (naive check)
        // If Tailwind CDN is present, we use type="text/tailwindcss" to allow @apply
        // Otherwise we use standard css
        const isTailwind = headContent.includes('tailwindcss');
        const styleTag = isTailwind 
            ? `<style type="text/tailwindcss">${cssContent}</style>`
            : `<style>${cssContent}</style>`;

        return `<!DOCTYPE html>
<html>
    <head>
        <!-- Dynamic Head from Settings -->
        ${headContent}
        
        <!-- Editor CSS -->
        ${styleTag}
    </head>
    <body>
        ${htmlContent}
        
        <!-- System Scripts -->
        <script type="module" src="/static/hikarin/main.js"></script>
        
        <!-- User Scripts (from Script Tab) -->
        <script>
        ${jsContent}
        </script>
    </body>
</html>`;
    },

    // --- AI Prompt Helpers ---

    async getPrompt() {
        const userHtml = this.editors.html.getValue();
        const userCss = this.editors.css.getValue();
        
        // Ensure we have latest head info for the AI context
        const response = await this.$api.aina.get(this.slug).execute();
        const head = response.custom?.builder?.header || "";
        
        return `Your task is to create a UI based on the given template.

Constraints:
1. Write HTML and CSS only.
2. Interactivity must use Alpine.js (assume imported).
3. Do NOT modify the <head>.

Context - The current <head> contains:
${head}

Current Code:
---
HTML:
${userHtml}

CSS:
${userCss}
---

Your task is: [TASK HERE]`;
    },

    async copyPrompt() {
        try {
            const text = await this.getPrompt();
            await navigator.clipboard.writeText(text);
            this.$store.notifications.add({ type: 'success', message: 'Prompt copied to clipboard' });
        } catch (err) {
            console.error('Failed to copy prompt', err);
        }
    }
});