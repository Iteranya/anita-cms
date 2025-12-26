// alpine/editorManager.js
export default function() {
    return {
        editorInstance: null,
        content: '# Hello World',

        async init() {
            // Find the container element (add x-ref="editor" to your HTML div)
            const element = this.$refs.editor;

            // Initialize Crepe
            this.editorInstance = await window.CrepeService.init(element, this.content, {
                // Callback to sync data back to Alpine data
                onChange: (markdown) => {
                    this.content = markdown;
                    // Optional: Auto-save trigger logic here
                }
            });
        },

        // Example: How to update content programmatically
        setContent(newMarkdown) {
            // Crepe doesn't have a simple .setValue(), you usually destroy/recreate 
            // OR use internal prosemirror commands, but for simple use cases:
            if(this.editorInstance) {
                // Access underlying editor to replace all (Advanced usage)
                // simpler approach for simple apps:
                // console.log("Crepe doesn't support simple external setValue yet without transaction logic");
            }
        },

        destroy() {
            if (this.editorInstance) {
                this.editorInstance.destroy();
            }
        }
    }
}