// notifications.js - Notification system
/**
 * Display a notification message to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of notification ('info', 'success', or 'error')
 */
export function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.innerHTML = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '70px';
    notification.style.right = '20px';
    notification.style.padding = '10px 20px';
    notification.style.borderRadius = '5px';
    notification.style.color = 'white';
    notification.style.zIndex = '30';
    
    // Set background color based on notification type
    if (type === 'success') {
        notification.style.backgroundColor = '#4CAF50';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#f44336';
    } else {
        notification.style.backgroundColor = '#2196F3';
    }
    
    // Style links inside the notification
    const links = notification.querySelectorAll('a');
    links.forEach(link => {
        link.style.color = 'white';
        link.style.textDecoration = 'underline';
        // Make sure links open in a new tab
        if (!link.hasAttribute('target')) {
            link.setAttribute('target', '_blank');
        }
    });
    
    document.body.appendChild(notification);
    
    // Remove notification after appropriate time
    const displayTime = type === 'success' ? 5000 : 3000;
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s';
        setTimeout(() => notification.remove(), 500);
    }, displayTime);
}