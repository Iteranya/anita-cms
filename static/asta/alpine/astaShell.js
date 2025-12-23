export default () => ({
    currentPath: window.location.pathname,

    init() {
        // Listen for HTMX navigation events to update the active tab
        document.body.addEventListener('htmx:afterSwap', (e) => {
            this.currentPath = e.detail.pathInfo.requestPath;
        });
    },
});