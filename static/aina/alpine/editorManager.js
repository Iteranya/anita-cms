export default (slug, initialData = {}) => ({
    slug: slug,
    isProcessing: false,
    statusText: 'Ready',
    editors: { html: null, css: null },
    
    // Config for compilation
    sysConfig: {
        head: `
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.tailwindcss.com"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"></script>
        `,
        defaultHtml: `<div class="p-10">\n  <h1 class="text-3xl font-bold text-blue-600">New Page</h1>\n  <p>Start editing...</p>\n</div>`,
        defaultCss: `body { background-color: #f3f4f6; }`
    },

    async init() {
        // 1. Initialize HTML Editor
        this.editors.html = window.AceService.init(
            this.$refs.htmlEditor, 
            'html', 
            initialData.html || this.sysConfig.defaultHtml
        );

        // 2. Initialize CSS Editor
        this.editors.css = window.AceService.init(
            this.$refs.cssEditor, 
            'css', 
            initialData.css || this.sysConfig.defaultCss
        );

        // 3. Initial Render from Server
        await this.fetchAndRender();
    },

    /**
     * ACTION 1: Run / Sync
     * 1. Updates 'custom.builder' on server (Source code).
     * 2. Calls fetchAndRender() to get that truth back and compile it.
     * Note: This DOES NOT update the public 'html' field.
     */
    async syncAndRender() {
        this.isProcessing = true;
        this.statusText = 'Syncing...';

        const userHtml = this.editors.html.getValue();
        const userCss = this.editors.css.getValue();

        // 1. Network Call (Get Script) - We still need this to mix in generator data
        const currentScript = (await this.$api.aina.get(this.slug).execute())?.custom?.builder?.script || "";

        // 2. Network Call (Save in Background!)
        const payload = {
            custom: {
                builder: {
                    head: this.sysConfig.head,
                    content: userHtml,
                    style: userCss,
                    script: currentScript
                }
            }
        };
        
        // START saving, but don't await it for the preview!
        const savePromise = this.$api.aina.updateHTML().execute(this.slug, payload);

        // 3. Render IMMEDIATELY using local variables
        const finalHtml = this.compilePage(userHtml, userCss, currentScript);
        this.$refs.previewFrame.srcdoc = finalHtml;
        
        // Now await the save just to update the "Saved" status text
        try {
            await savePromise;
            this.statusText = 'Saved';
        } catch (e) {
            this.statusText = 'Save Failed';
        }
        
        this.isProcessing = false;
    },

    /**
     * ACTION 2: Deploy
     * Compiles the current editor state into a full HTML string
     * and saves it to the 'html' field on the server.
     */
    async deployHtml() {
        this.isProcessing = true;
        this.statusText = 'Deploying...';
        const response = await this.$api.aina.get(this.slug).execute();
        const builderData = response.custom?.builder || {};
        const script = builderData.script || ""

        const userHtml = this.editors.html.getValue();
        const userCss = this.editors.css.getValue();
        const generatedJs = script
        
        // Compile locally just for the payload construction
        const fullCompiledHtml = this.compilePage(userHtml, userCss, generatedJs);

        const payload = {
            html: fullCompiledHtml
        };

        try {
            await this.$api.aina.updateHTML().execute(this.slug, payload);
            
            this.$store.notifications.add({
                type: 'success',
                title: 'Deployed',
                message: 'Public HTML has been updated.'
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
     * Fetches the page object from server, extracts builder data,
     * compiles it, and updates the iframe.
     */
    async fetchAndRender() {
        try {
            // 1. GET request (Single Source of Truth)
            const response = await this.$api.aina.get(this.slug).execute();
            
            // 2. Extract Data (fallback to current editor values if server is empty/new)
            const builderData = response.custom?.builder || {};
            
            const content = builderData.content || this.editors.html.getValue();
            const style = builderData.style || this.editors.css.getValue();
            const script = builderData.script || ""

            if (content) {
                this.editors.html.setValue(content, -1);
            }
                
            if (style) {
                this.editors.css.setValue(style, -1);
            }

            // 3. Compile everything together
            const finalHtml = this.compilePage(content, style, script);

            // 4. Update Iframe
            if (this.$refs.previewFrame) {
                this.$refs.previewFrame.srcdoc = finalHtml;
            }
        } catch (error) {
            console.error("Fetch render error:", error);
        }
    },

    /**
     * Helper to combine Head, Style, and Body
     */
    compilePage(htmlContent, cssContent, jsContent) {
        const result = `<!DOCTYPE html>
<html>
    <head>
        ${this.sysConfig.head}
        <style type="text/tailwindcss">${cssContent}</style>
    </head>
    <body>
        ${htmlContent}
        <script>
        ${jsContent}
        </script>
    </body>
</html>`
        console.log(result)
        return result;
    }
});