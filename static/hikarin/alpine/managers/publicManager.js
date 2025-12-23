export default () => ({
    // --- State ---
    
    // Single Page Data
    page: null,           
    
    // Search Data
    searchResults: [],    
    searchQuery: '',      
    
    // HTML Content (Hydration)
    htmlContent: '',      
    
    // UI State
    isLoading: false,
    error: null,          
    statusCode: null,     

    // --- Lifecycle ---

    init() {
        // Optional: Load initial data if needed
    },

    // --- JSON Data Methods ---

    /**
     * Fetch a top-level page by slug
     */
    async loadPage(slug) {
        this._startLoading();
        try {
            this.page = await this.$api.public.get(slug).execute();
        } catch (e) {
            this._handleError(e, 'Failed to load page');
        } finally {
            this.isLoading = false;
        }
    },

    /**
     * Fetch a nested page by category and slug
     */
    async loadPageByCategory(category, slug) {
        this._startLoading();
        try {
            this.page = await this.$api.public.getByCategory(category, slug).execute();
        } catch (e) {
            this._handleError(e, 'Failed to load nested page');
        } finally {
            this.isLoading = false;
        }
    },

    /**
     * Search pages by tags.
     * If explicitTags is provided, uses that.
     * Otherwise parses this.searchQuery.
     * If query is empty, passes [] to the route.
     */
    async search(explicitTags = null) {
        this._startLoading();
        
        let tags = [];

        // 1. Determine Tag Source
        if (Array.isArray(explicitTags)) {
            // Case A: Explicit array passed via function argument
            tags = explicitTags;
        } else {
            // Case B: Parse from bound input model
            const rawInput = (this.searchQuery || '').trim();
            
            if (rawInput.length > 0) {
                tags = rawInput
                    .split(',')
                    .map(t => t.trim())
                    .filter(t => t.length > 0);
            }
            // If rawInput is empty, tags remains []
        }

        try {
            // 2. Execute API Call with the array (empty or populated)
            // This ensures the route receives [] if search is empty
            this.searchResults = await this.$api.public.search(tags).execute();
            
        } catch (e) {
            this._handleError(e, 'Search failed');
            this.searchResults = []; // Ensure results are cleared on error
        } finally {
            this.isLoading = false;
        }
    },

    // --- Raw HTML Methods ---

    async loadHomeHtml() {
        this._startLoading();
        try {
            this.htmlContent = await this.$api.public.getHomeHtml().execute();
        } catch (e) { this._handleError(e); } 
        finally { this.isLoading = false; }
    },

    async loadPageHtml(slug) {
        this._startLoading();
        try {
            this.htmlContent = await this.$api.public.getTopLevelHtml(slug).execute();
        } catch (e) { this._handleError(e); } 
        finally { this.isLoading = false; }
    },

    // --- Helpers ---

    clear() {
        this.page = null;
        this.searchResults = [];
        this.htmlContent = '';
        this.error = null;
        this.statusCode = null;
        // Optional: Clear the search box too
        // this.searchQuery = ''; 
    },

    _startLoading() {
        this.isLoading = true;
        this.error = null;
        this.statusCode = null;
    },

    _handleError(e, contextMsg = 'Error') {
        console.error(`${contextMsg}:`, e);
        this.error = e.message || 'Unknown error occurred';
        this.statusCode = e.status || 500;
        
        if (Alpine.store('notifications')) {
            Alpine.store('notifications').error(contextMsg, e);
        }
    },

    isCurrent(slug) {
        return this.page && this.page.slug === slug;
    }
});