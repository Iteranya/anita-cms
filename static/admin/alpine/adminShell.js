export default () => ({
    sidebarOpen: true,
    currentPath: window.location.pathname,

    init() {
        // Listen for HTMX navigation events to update the active tab
        document.body.addEventListener('htmx:afterSwap', (e) => {
            this.currentPath = e.detail.pathInfo.requestPath;
        });
    },

    toggleSidebar() {
        console.log("Toggling sidebar...", this.sidebarOpen); // Debug line
        this.sidebarOpen = !this.sidebarOpen;
    },

    isActive(path) {
        return this.currentPath.includes(path);
    }
});