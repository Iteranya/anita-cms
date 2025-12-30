// asta/alpine/generatorManager.js
export default () => ({
    // --- Core Data ---
    isLoading: false,
    embeds: [],
    categories: {},

    // --- UI State ---
    activeCategory: 'All',
    searchQuery: '',

    async init() {
        await this.fetchEmbeds();
    },

    // --- Data Fetching ---
    async fetchEmbeds() {
        this.isLoading = true;
        try {
            // Uses the API defined in asta/main.js
            const data = await this.$api.asta.getEmbeds().execute();
            this.embeds = data;
            
            // Group by Category
            this.categories = data.reduce((acc, item) => {
                const cat = item.category || 'Uncategorized';
                if (!acc[cat]) acc[cat] = [];
                acc[cat].push(item);
                return acc;
            }, {});
        } catch (error) {
            console.error("Embeds load error", error);
            this.$store.notifications.add({ type: 'error', message: 'Failed to load embeds.' });
        } finally {
            this.isLoading = false;
        }
    },

    // --- Getters ---
    get filteredItems() {
        let items = this.embeds;
        
        // Filter by Category
        if (this.activeCategory !== 'All') {
            items = items.filter(r => (r.category || 'Uncategorized') === this.activeCategory);
        }
        
        // Filter by Search
        if (this.searchQuery) {
            const q = this.searchQuery.toLowerCase();
            items = items.filter(r => 
                r.name.toLowerCase().includes(q) || 
                (r.description && r.description.toLowerCase().includes(q))
            );
        }
        
        return items;
    },

    // --- Actions ---

    /**
     * Helper to get the content string for a specific slug.
     */
    getEmbedContent(slug) {
        const item = this.embeds.find(i => i.slug === slug);
        return item ? item.data : '';
    },

    /**
     * Primary Action: Dispatches an event with the content.
     * The EditorShell or EditorManager should listen for 'insert-content'.
     */
    insert(slug) {
        const content = this.getEmbedContent(slug);
        if (!content) return;

        // Dispatch event for editorManager to catch
        window.dispatchEvent(new CustomEvent('asta:insert', { 
            detail: { content: content } 
        }));

        this.$store.notifications.add({ 
            type: 'info', 
            message: 'Inserted ' + slug 
        });
    },

    /**
     * Fallback: Copy to clipboard if needed manually
     */
    async copy(slug) {
        const content = this.getEmbedContent(slug);
        try {
            await navigator.clipboard.writeText(content);
            this.$store.notifications.add({ type: 'success', message: 'Copied to clipboard' });
        } catch (err) {
            console.error('Copy failed', err);
        }
    }
});