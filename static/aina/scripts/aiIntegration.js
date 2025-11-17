// aiIntegration.js - AI generation integration
import { showNotification } from './notifications.js';

/**
 * Initialize the AI generation functionality
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor
 * @param {Function} updatePreviewCallback - Function to refresh the preview
 * @param {HTMLTextAreaElement} [notesArea] - Optional notes textarea (for extra context)
 */
export function initAiGeneration(htmlCode, updatePreviewCallback, notesArea) {
    const form = document.querySelector('form');
    if (!form) {
        console.warn("⚠️ No form element found for AI generation.");
        return;
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const button = form.querySelector('button');
        const originalButtonText = button.innerHTML;

        // Loading state
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

        const promptInput = form.querySelector('[name="content"]');
        const promptText = promptInput ? promptInput.value : "";
        const notesText = notesArea ? notesArea.value : ""; // ✅ Safe access
        const fullPrompt = notesText + "\n\n" + promptText ;

        const editor = htmlCode.value;

        try {
            const response = await fetch('/aina/generate-website-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ editor, prompt: fullPrompt })
            });

            if (!response.ok)
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);

            const reader = response.body.getReader();
            let generatedHtml = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunkText = new TextDecoder().decode(value);
                generatedHtml += chunkText;

                htmlCode.value = generatedHtml;
                updatePreviewCallback(htmlCode, document.getElementById('preview'));
            }

            showCompletionEffect();
        } catch (error) {
            console.error('Error:', error);
            showNotification('Yabai! Something went wrong (╥﹏╥)', 'error');
        } finally {
            button.disabled = false;
            button.innerHTML = originalButtonText;
        }
    });
}

/**
 * Shows a cute completion animation when generation finishes 💫
 */
function showCompletionEffect() {
    const completionEffect = document.createElement('div');
    completionEffect.textContent = '✧･ﾟ: *✧･ﾟ:* Generation Complete! *:･ﾟ✧*:･ﾟ✧';
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
    setTimeout(() => completionEffect.remove(), 3000);
}
