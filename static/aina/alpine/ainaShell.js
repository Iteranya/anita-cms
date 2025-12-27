export default () => ({
    currentPath: window.location.pathname,

    init() {
        // 1. Listen for HTMX updating the history (clicking a link)
        document.body.addEventListener('htmx:pushedIntoHistory', () => {
            this.currentPath = window.location.pathname;
        });

        // 2. Listen for Browser Back/Forward buttons
        window.addEventListener('popstate', () => {
            this.currentPath = window.location.pathname;
        });
        
        // 3. (Optional) Catch-all for when content is swapped but URL might stay same
        // or to force update on standard hx-swaps
        document.body.addEventListener('htmx:afterOnLoad', () => {
             // Slight delay to ensure window.location is updated
             requestAnimationFrame(() => {
                 this.currentPath = window.location.pathname;
             });
        });
    },

    // Helper to keep HTML clean
    isActive(route) {
        return this.currentPath.includes(route);
    }
});