// aiIntegration.js
import { showNotification } from './notifications.js';
import { initContextManager, getEngineeredContext } from './contextManager.js';

// Track current stream state
let currentReader = null;
let isGenerating = false;

/**
 * Initialize the AI generation functionality
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor
 * @param {Function} updatePreviewCallback - Function to refresh the preview
 */
export async function initAiGeneration(htmlCode, updatePreviewCallback) {
    
    // 1. Initialize the Context Manager (Dropdowns, Image Picker, etc.)
    await initContextManager();

    const form = document.getElementById('generator-form');
    if (!form) {
        console.warn("⚠️ No generator form found.");
        return;
    }

    // 3. Handle Form Submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const button = document.getElementById('generate-btn') || form.querySelector('button');
        
        // If already generating, stop it
        if (isGenerating) {
            await stopGeneration(button);
            return;
        }

        const originalButtonHtml = button.innerHTML;

        // UI: Set Loading State
        button.disabled = false; // Keep enabled so user can click to stop
        button.innerHTML = '<i class="fas fa-stop-circle"></i> Stop';
        button.classList.add('pulsing'); // Add a CSS animation class if you have one
        isGenerating = true;

        // 🧠 PROMPT ENGINEERING LOGIC 🧠
        const promptInput = form.querySelector('[name="content"]');
        const userPrompt = promptInput ? promptInput.value : "";

        // Get the hidden context (Routes schemas + Image Metadata)
        const contextData = getEngineeredContext();

        // Combine them for the AI
        const fullPrompt = `${contextData}\n\n### USER REQUEST ###\n${userPrompt}`;

        console.log("🚀 Sending Prompt to AI:", fullPrompt); // Debug log to see what goes out

        const editorContent = htmlCode.value;

        try {
            const response = await fetch('/aina/generate-website-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ editor: editorContent, prompt: fullPrompt })
            });

            if (!response.ok)
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);

            currentReader = response.body.getReader();
            let generatedHtml = '';

            // Stream Loop
            while (true) {
                const { done, value } = await currentReader.read();
                if (done) break;

                const chunkText = new TextDecoder().decode(value);
                generatedHtml += chunkText;

                // Update Editor and Preview
                htmlCode.value = generatedHtml;
                if (updatePreviewCallback) updatePreviewCallback(htmlCode, document.getElementById('preview'));
            }

            showCompletionEffect();

        } catch (error) {
            if (error.name === 'AbortError') {
                showNotification('Generation stopped! (｡•́︿•̀｡)', 'info');
            } else {
                console.error('Error:', error);
                showNotification('Yabai! Something went wrong (╥﹏╥)', 'error');
            }
        } finally {
            // Reset UI
            isGenerating = false;
            currentReader = null;
            button.disabled = false;
            button.innerHTML = originalButtonHtml;
            button.classList.remove('pulsing');
        }
    });
}

/**
 * Handles the sidebar logic (Moved here from formIntegration.js)
 */
function setupSidebarToggle() {
    const sidebar = document.getElementById('notes-sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const mediaDrawer = document.getElementById('media-picker-drawer');

    if (sidebar && toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            document.body.classList.toggle('sidebar-open');
            
            // UX: Close the media drawer if we close the main sidebar
            if (!sidebar.classList.contains('open') && mediaDrawer) {
                mediaDrawer.classList.add('hidden');
            }
        });
    }
}

/**
 * Stop the current generation
 */
async function stopGeneration(button) {
    if (currentReader) {
        try {
            await currentReader.cancel(); // Cancel the stream reader
            
            // Notify backend to stop
            await fetch('/aina/stop-website-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            showNotification('Stopped generation ヾ(•ω•`)o', 'info');
        } catch (error) {
            console.error('Error stopping generation:', error);
        }
    }
    
    isGenerating = false;
    currentReader = null;
}

/**
 * Shows a cute completion animation when generation finishes 💫
 */
function showCompletionEffect() {
    const completionEffect = document.createElement('div');
    completionEffect.textContent = '✧･ﾟ: *✧･ﾟ:* Generation Complete! *:･ﾟ✧*:･ﾟ✧';
    
    // Inline styles for the popup
    Object.assign(completionEffect.style, {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: 'rgba(76, 175, 80, 0.9)',
        color: 'white',
        padding: '10px 20px',
        borderRadius: '20px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
        animation: 'fadeInOut 3s ease-out',
        zIndex: '1000',
        pointerEvents: 'none'
    });

    // Animation keyframes need to exist in CSS, or we can use transition
    document.body.appendChild(completionEffect);
    setTimeout(() => completionEffect.remove(), 3000);
}