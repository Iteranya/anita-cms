// settingsManager.js - Settings management
import { showNotification } from './notifications.js';

// Config form elements
let settingsPanel;
let aiSetupForm;
let endpointInput;
let modelInput;
let tempInput;
let systemPromptInput;
let apiKeyInput;

/**
 * Initialize the settings manager
 */
export function initSettingsManager() {
    // Get references to form elements
    settingsPanel = document.getElementById('settings-panel');
    aiSetupForm = document.getElementById('ai-setup-form');
    endpointInput = document.getElementById('ai-endpoint');
    modelInput = document.getElementById('ai-model');
    tempInput = document.getElementById('ai-temp');
    systemPromptInput = document.getElementById('system-prompt');
    apiKeyInput = document.getElementById('ai-key');

    // Load initial configuration
    loadConfig();
    
    // Set up form submission
    aiSetupForm.addEventListener('submit', saveConfig);
    
    // Add reset button
    addResetButton();
}

/**
 * Load configuration from server
 */
async function loadConfig() {
    try {
        const response = await fetch('/config');
        if (!response.ok) {
            throw new Error(`Error fetching config: ${response.statusText}`);
        }
        
        const config = await response.json();
        
        // Populate form with current values
        endpointInput.value = config.ai_endpoint || '';
        modelInput.value = config.base_llm || '';
        tempInput.value = config.temperature || '';
        systemPromptInput.value = config.system_note || '';
        apiKeyInput.value = ""; // Don't populate API key for security
        
    } catch (error) {
        console.error('Failed to load configuration:', error);
        showNotification('Failed to load configuration', 'error');
    }
}

/**
 * Save configuration to server
 * @param {Event} event - Form submission event
 */
async function saveConfig(event) {
    event.preventDefault();
    
    const configData = {
        ai_endpoint: endpointInput.value,
        base_llm: modelInput.value,
        temperature: parseFloat(tempInput.value) || 0.7,
        system_note: systemPromptInput.value,
        ai_key: apiKeyInput.value
    };
    
    try {
        const response = await fetch('/config', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update configuration');
        }
        
        showNotification('Configuration saved successfully', 'success');
        settingsPanel.style.display = 'none';
        
    } catch (error) {
        console.error('Failed to save configuration:', error);
        showNotification(error.message, 'error');
    }
}

/**
 * Add reset button to the form
 */
function addResetButton() {
    const resetButton = document.createElement('button');
    resetButton.innerHTML = '<i class="fas fa-undo"></i> Reset';
    resetButton.type = 'button';
    resetButton.style.marginLeft = '10px';
    resetButton.style.backgroundColor = '#f44336';
    resetButton.style.color = 'white';
    resetButton.style.border = 'none';
    resetButton.style.borderRadius = '5px';
    resetButton.style.padding = '5px 10px';
    resetButton.style.cursor = 'pointer';
    
    const submitButton = aiSetupForm.querySelector('button[type="submit"]');
    submitButton.parentNode.insertBefore(resetButton, submitButton.nextSibling);
    
    resetButton.addEventListener('click', resetConfig);
}

/**
 * Reset configuration to defaults
 */
async function resetConfig() {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
        try {
            const response = await fetch('/config/reset', {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to reset configuration');
            }
            
            showNotification('Configuration reset to defaults', 'success');
            loadConfig(); // Reload the form with default values
            
        } catch (error) {
            console.error('Failed to reset configuration:', error);
            showNotification(error.message, 'error');
        }
    }
}