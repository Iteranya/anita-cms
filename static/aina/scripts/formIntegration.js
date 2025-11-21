// aiIntegration.js
import { showNotification } from './notifications.js';
import { initContextManager, getEngineeredContext } from './contextManager.js';

// Track current stream state
let currentReader = null;
let isGenerating = false;

/**
 * Initialize the AI generation functionality and UI components
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor
 * @param {Function} updatePreviewCallback - Function to refresh the preview
 */
export async function initAiGeneration(htmlCode, updatePreviewCallback) {
    
    // 1. Initialize the new Context Manager (Dropdowns & Image Picker)
    await initContextManager();

    // 2. Initialize Sidebar Toggle (Replaces formIntegration.js logic)
    initSidebarToggle();

    // 3. Setup Form Submission
    const form = document.getElementById('generator-form');
    if (!form) {
        console.warn("⚠️ No generator form found.");
        return;
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const button = document.getElementById('generate-btn');
        
        // If already generating, stop it
        if (isGenerating) {
            await stopGeneration(button);
            return;
        }

        // Save original text to restore later
        const originalButtonHtml = button.innerHTML;

        // UI: Loading state
        button.disabled = false; // Keep enabled so user can click to stop
        button.innerHTML = '<i class="fas fa-stop-circle"></i> Stop';
        button.classList.add('pulse-animation'); // Optional CSS class for effect
        isGenerating = true;

        // 🧠 PREPARE THE PROMPT
        const promptInput = form.querySelector('[name="content"]');
        const userPrompt = promptInput ? promptInput.value : "";
        
        // Get the invisible context from our new Manager
        const systemContext = getEngineeredContext();
        
        // Combine: Context + User Input
        const fullPrompt = `${systemContext}\n\nUSER REQUEST:\n${userPrompt}`;

        console.log("📝 Sending Prompt with Context:", fullPrompt);

        const editor = htmlCode.value;

        try {
            const response = await fetch('/aina/generate-website-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ editor, prompt: fullPrompt })
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

                // Update CodeMirror/Textarea
                htmlCode.value = generatedHtml;
                // Update Live Preview
                updatePreviewCallback(htmlCode, document.getElementById('preview'));
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
            // Cleanup / Reset UI
            isGenerating = false;
            currentReader = null;
            button.disabled = false;
            button.innerHTML = originalButtonHtml;
            button.classList.remove('pulse-animation');
        }
    });
}

/**
 * Handles the sidebar opening/closing
 * (Replaces the logic previously found in formIntegration.js)
 */
function initSidebarToggle() {
    const sidebar = document.getElementById('notes-sidebar'); // Assuming you kept the ID on the parent
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (sidebar && toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            document.body.classList.toggle('sidebar-open');
        });
        
        // Optional: Close media drawer if sidebar closes
        const mediaDrawer = document.getElementById('media-picker-drawer');
        if(mediaDrawer && !sidebar.classList.contains('open')) {
            mediaDrawer.classList.add('hidden');
        }
    }
}

/**
 * Stop the current generation
 */
async function stopGeneration(button) {
    if (currentReader) {
        try {
            await currentReader.cancel(); 
            
            // Notify backend to stop processing
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
        zIndex: '1000'
    });

    document.body.appendChild(completionEffect);
    setTimeout(() => completionEffect.remove(), 3000);
}