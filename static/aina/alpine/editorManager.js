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
    ...initialData, // Spread existing data
        
        // Layout State
        leftWidth: 40, // Percentage width of editor column
        cssHeight: 35, // Percentage height of CSS editor
        showCss: true,
        showPreview: true,
        
        // Drag State
        dragType: null, // 'horizontal' or 'vertical'
        
        // Existing state
        isProcessing: false,
        copiedPrompt: false,
        statusText: 'Ready',
        slug: slug,

        toggleCss() {
            this.showCss = !this.showCss;
            // Resize logic could go here if you want auto-adjust
        },

        togglePreview() {
            this.showPreview = !this.showPreview;
            if (this.showPreview && this.leftWidth > 90) {
                this.leftWidth = 50; // Reset if it was too wide
            }
        },

        startDrag(e, type) {
            this.dragType = type;
            document.body.style.cursor = type === 'horizontal' ? 'col-resize' : 'row-resize';
        },

        stopDrag() {
            this.dragType = null;
            document.body.style.cursor = 'default';
        },

        handleDrag(e) {
            if (!this.dragType) return;

            const container = this.$refs.workspaceContainer;
            const containerRect = container.getBoundingClientRect();

            if (this.dragType === 'horizontal') {
                // Calculate percentage of total width
                let newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
                
                // Constraints (10% to 90%)
                if (newWidth < 10) newWidth = 10;
                if (newWidth > 90) newWidth = 90;
                
                this.leftWidth = newWidth;
            }

            if (this.dragType === 'vertical') {
                // Vertical is tricky because CSS pane is at bottom.
                // We calculate how much height the CSS pane should have based on mouse Y.
                // Note: e.clientY is global.
                
                let relativeY = e.clientY - containerRect.top;
                let percentageY = (relativeY / containerRect.height) * 100;

                // Since CSS is at the bottom, its height is roughly (100 - percentageY)
                // However, percentageY is where the mouse IS. Ideally, the mouse is on the split line.
                // So the TOP pane takes `percentageY`, and CSS takes remainder.
                
                let newCssHeight = 100 - percentageY;

                // Constraints (10% to 80%)
                if (newCssHeight < 5) newCssHeight = 5;
                if (newCssHeight > 80) newCssHeight = 80;

                this.cssHeight = newCssHeight;
            }
            
            // Trigger editor resize if using Monaco/Ace so they redraw
            // window.dispatchEvent(new Event('resize')); 
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
     * TODO: Replace tailwind compilation scrape from iFrame with Tailwind CLI
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

    async copyPrompt() {
        try {
            // Generate the prompt text using your existing method
            const promptText = await this.getPrompt();

            // Write to system clipboard
            await navigator.clipboard.writeText(promptText);

            // Trigger UI feedback
            this.copiedPrompt = true;
            
            // Reset button state after 2 seconds
            setTimeout(() => {
                this.copiedPrompt = false;
            }, 2000);

        } catch (err) {
            console.error('Failed to copy prompt:', err);
            this.$store.notifications.add({ 
                type: 'error', 
                message: 'Failed to copy to clipboard.' 
            });
        }
    },

    async getPrompt() {
        const userHtml = this.editors.html.getValue();
        const userCss = this.editors.css.getValue();
        const response = await this.$api.aina.get(this.slug).execute();
        const head = response.custom?.builder?.header || "";
        
        return `Your task is to create a UI partial based on the data.
Constraints:
1. Write HTML and Tailwind CSS only.
2. Interactivity must use Alpine.js no <script> tags.
3. Do NOT modify the <head>.

Context - The current <head> contains:
${head}

Current Code:
---
HTML:
${userHtml}

CSS:
${userCss}

JS:
${this.currentScript}
---

Your task is: [TASK HERE]`;
    }
});