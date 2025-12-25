export default () => ({
    init() {
        console.log("Hikarin Shell: Initialized");

        // Delay slightly to ensure Alpine magic ($api) is fully bound 
        // before we fetch content that might rely on x-init="$api..."
        this.$nextTick(() => {
            this.loadInitialView();
        });
    },

    loadInitialView() {
        // 1. Get current path (e.g., /auth/login)
        const path = window.location.pathname;

        // 2. Ensure we are actually in the auth flow
        if (path.includes('/auth/')) {
            console.log("Hikarin Shell: Loading view for", path);
            
            // 3. Add timestamp to bust cache for the HTML partial
            const antiCacheUrl = path + "?t=" + Date.now();

            // 4. Manual HTMX trigger
            htmx.ajax('GET', antiCacheUrl, {
                target: '#app-content',
                swap: 'innerHTML transition:true' 
            });
        }
    }
});