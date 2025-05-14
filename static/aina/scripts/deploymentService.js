// deploymentService.js - Deployment functionality
import { showNotification } from './notifications.js';

/**
 * Set up deployment functionality
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor element
 */
export function setupDeployment(htmlCode) {
    // Open deployment modal
    document.getElementById('deploy-btn').addEventListener('click', () => {
        document.getElementById('deploy-modal').style.display = 'block';
    });

    // Handle deployment confirmation
    document.getElementById('confirm-deploy').addEventListener('click', async () => {
        const title = document.getElementById('site-title').value;
        const content = htmlCode.value;
        
        if (!title) {
            alert('Please enter a site title!');
            return;
        }

        try {
            const response = await fetch('/save-html', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content,
                    title: title
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                showNotification(`Site deployed successfully! 🎉 Access it at <a href="/${result.path}" target="_blank">${result.path}</a>`, 'success');
            } else {
                showNotification(`Deployment failed: ${result.detail}`, 'error');
            }
        } catch (error) {
            console.error('Deployment error:', error);
            showNotification('Yabai! Deployment failed (╥﹏╥)', 'error');
        }
        
        document.getElementById('deploy-modal').style.display = 'none';
        document.getElementById('site-title').value = '';
    });
}