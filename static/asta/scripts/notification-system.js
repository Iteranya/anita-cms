// notification-system.js
// System for displaying temporary notifications

export class NotificationSystem {
    /**
     * Shows a temporary notification message.
     * @param {string} message - The message to display.
     * @param {'success' | 'error'} type - The type of notification.
     */
    static show(message, type = 'success') {
        // Always get or create the container
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = message;
        container.appendChild(notification);
        
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });
        
        setTimeout(() => {
            notification.classList.remove('show');
            notification.classList.add('hide');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}