//aina
export default (slug, initialData = {}) => ({
    slug: slug,
    isProcessing: false,
    statusText: 'Ready',
    editors: { html: null, css: null },
    
    // Internal State
    currentHead: '',
    currentScript: '',
    
    defaults: {
        html: `<div class="p-10">\n  <h1 class="text-3xl font-bold text-blue-600">New Page</h1>\n  <p>Start editing...</p>\n</div>`,
        css: `body { background-color: #f3f4f6; }`
    },

    async init() {
        this.editors.html = window.AceService.init(this.$refs.htmlEditor, 'html', initialData.html || this.defaults.html);
        this.editors.css = window.AceService.init(this.$refs.cssEditor, 'css', initialData.css || this.defaults.css);
        await this.fetchAndRender();
    },

    async syncAndRender() {
        this.isProcessing = true;
        this.statusText = 'Syncing...';
        const userHtml = this.editors.html.getValue();
        const userCss = this.editors.css.getValue();

        try {
            const currentData = await this.$api.aina.get(this.slug).execute();
            const builder = currentData.custom?.builder || {};
            
            this.currentHead = builder.header || '';
            this.currentScript = builder.script || '';

            const payload = {
                custom: {
                    builder: {
                        ...builder,
                        content: userHtml,
                        style: userCss,
                        header: this.currentHead, 
                        script: this.currentScript
                    }
                }
            };
            
            const savePromise = this.$api.aina.updateHTML().execute(this.slug, payload);
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
     * MODIFIED: Deploy Logic
     * Grabs the *already rendered* styles from the active preview iframe.
     * TODO: Replace tailwind scrape from iFrame with Tailwind CLI
     */
    async deployHtml() {
        this.isProcessing = true;
        this.statusText = 'Compiling...';

        try {
            // 1. Fetch Source of Truth for Head/Script (things not in the editor)
            const response = await this.$api.aina.get(this.slug).execute();
            const builder = response.custom?.builder || {};
            
            const headRaw = builder.header || '';
            const script = builder.script || '';
            const html = this.editors.html.getValue();

            // 2. Extract CSS directly from the EXISTING iframe
            const compiledCss = this.getGeneratedStylesFromIframe();
            if (!compiledCss && headRaw.includes('tailwindcss')) {
                console.warn("Tailwind detected but no styles found. The iframe might be reloading.");
                this.$store.notifications.add({ 
                    type: 'warning', 
                    message: 'Warning: No styles detected. Is the preview loaded?' 
                });
            }

            // 3. Clean the Head (Remove the Tailwind CDN Script)
            const productionHead = this.stripTailwindScript(headRaw);

            // 4. Build Production HTML (Inline Compiled CSS)
            const productionHtml = `<!DOCTYPE html>
<html>
    <head>
        ${productionHead}
        <style>
            /* Compiled Output (Snapshot from Editor) */
            ${compiledCss}
        </style>
    </head>
    <body>
        ${html}
        
        <script type="module" src="/static/hikarin/main.js"></script>
        <script>
        ${script}
        </script>
    </body>
</html>`;

            // 5. Update Public HTML
            await this.$api.aina.updateHTML().execute(this.slug, { html: productionHtml });
            
            this.$store.notifications.add({
                type: 'success',
                title: 'Deployed',
                message: 'Site snapshot deployed successfully.'
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
     * Scrapes the contents of all <style> labels inside the preview iframe.
     * Iterates explicitly to ensure we catch Tailwind's injected styles.
     */
    getGeneratedStylesFromIframe() {
        const iframe = this.$refs.previewFrame;
        // Ensure iframe is loaded and accessible
        if (!iframe || !iframe.contentDocument || !iframe.contentDocument.body) {
            return '';
        }

        // Get all style labels (Includes user CSS and Tailwind generated CSS)
        const styleLabels = iframe.contentDocument.querySelectorAll('style');
        
        // Use Array.from to map nicely, filter out empty labels if needed
        return Array.from(styleLabels)
            .map(label => label.innerHTML)
            .join('\n');
    },

    // --- Helpers for Compilation ---

    /**
     * Scrapes the contents of all <style> labels inside the preview iframe.
     * The Tailwind CDN injects its generated CSS into a style label here.
     */
    getGeneratedStylesFromIframe() {
        const iframe = this.$refs.previewFrame;
        if (!iframe || !iframe.contentDocument) return '';

        // Get all style labels (Includes user CSS and Tailwind generated CSS)
        const styleLabels = iframe.contentDocument.querySelectorAll('style');
        
        let allStyles = '';
        styleLabels.forEach(label => {
            allStyles += label.innerHTML + '\n';
        });

        return allStyles;
    },

    /**
     * Removes the Tailwind CDN script label from the header string
     * so it doesn't run in production.
     */
    stripTailwindScript(headContent) {
        // Regex looks for <script src="...tailwindcss..."></script>
        // It handles both double and single quotes.
        return headContent.replace(/<script\s+[^>]*src=["'][^"']*\/static\/hikarin\/lib\/tailwind\.js["'][^>]*>[\s\S]*?<\/script>/gi, '');
    },

    // --- Standard Methods ---

    async fetchAndRender() {
        try {
            const response = await this.$api.aina.get(this.slug).execute();
            const builder = response.custom?.builder || {};
            
            this.currentHead = builder.header || '';
            this.currentScript = builder.script || '';
            
            if (builder.content) this.editors.html.setValue(builder.content, -1);
            if (builder.style) this.editors.css.setValue(builder.style, -1);

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

    updatePreview(html, css, head, script) {
        if (this.$refs.previewFrame) {
            this.$refs.previewFrame.srcdoc = this.compilePreviewPage(html, css, head, script);
        }
    },

    /**
     * Used ONLY for the Editor Preview (keeps Tailwind CDN active)
     */
    compilePreviewPage(htmlContent, cssContent, headContent, jsContent) {
        const isTailwind = headContent.includes('tailwindcss');
        // If Tailwind is present, we use the special type to let the CDN process @apply
        const styleLabel = isTailwind 
            ? `<style type="text/tailwindcss">${cssContent}</style>`
            : `<style>${cssContent}</style>`;

        return `<!DOCTYPE html>
<html>
    <head>
        ${headContent}
        ${styleLabel}
    </head>
    <body>
        ${htmlContent}
        <script type="module" src="/static/hikarin/main.js"></script>
        <script>
        ${jsContent}
        </script>
    </body>
</html>`;
    },

    async getPrompt() {
        const userHtml = this.editors.html.getValue();
        const userCss = this.editors.css.getValue();
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