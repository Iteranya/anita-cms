// aiIntegration.js - Simplified AI generation functionality
import { updatePreview } from './main.js';
import { showNotification } from './notifications.js';

/**
 * Initialize the AI generation functionality
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor element
 * @param {Function} updatePreviewCallback - Callback to update the preview
 */
export function initAiGeneration(htmlCode, updatePreviewCallback) {
    const form = document.querySelector('form');
   
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
       
        const button = form.querySelector('button');
        const originalButtonText = button.innerHTML;
       
        // Show loading state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
       
        const prompt = form.querySelector('[name="content"]').value;
        const editor = htmlCode.value;
       
        try {
            const response = await fetch('/aina/generate-website-stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    editor,
                    prompt
                })
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }

            const reader = response.body.getReader();
            let generatedHtml = '';
            
            // Process the stream
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    break;
                }
                
                // Convert the chunk to text
                const chunkText = new TextDecoder().decode(value);
                generatedHtml += chunkText;
                
                // Update the editor and preview with each chunk
                htmlCode.value = generatedHtml;
                updatePreviewCallback(htmlCode, document.getElementById('preview'));
            }
            
            // Show completion effect
            showCompletionEffect();
            
        } catch (error) {
            console.error('Error:', error);
            showNotification('Yabai! Something went wrong (╥﹏╥)', 'error');
        } finally {
            // Reset button state
            button.disabled = false;
            button.innerHTML = originalButtonText;
        }
    });
}

/**
 * Shows a completion effect animation
 */
function showCompletionEffect() {
    const completionEffect = document.createElement('div');
    completionEffect.innerHTML = '✧･ﾟ: *✧･ﾟ:* Generation Complete! *:･ﾟ✧*:･ﾟ✧';
    completionEffect.style.position = 'fixed';
    completionEffect.style.bottom = '20px';
    completionEffect.style.left = '50%';
    completionEffect.style.transform = 'translateX(-50%)';
    completionEffect.style.backgroundColor = 'rgba(76, 175, 80, 0.9)';
    completionEffect.style.color = 'white';
    completionEffect.style.padding = '10px 20px';
    completionEffect.style.borderRadius = '20px';
    completionEffect.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
    completionEffect.style.animation = 'fadeInOut 3s ease-out';
    completionEffect.style.zIndex = '1000';
    
    document.body.appendChild(completionEffect);
    
    setTimeout(() => {
        completionEffect.style.animation = 'fadeOut 0.5s ease-out';
        setTimeout(() => completionEffect.remove(), 500);
    }, 2500);
}