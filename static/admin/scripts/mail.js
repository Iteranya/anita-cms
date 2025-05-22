import { showToast } from './toastService.js';
// Get form references

const systemNoteField = document.getElementById('system-note');
const aiEndpointField = document.getElementById('ai-endpoint');
const baseLlmField = document.getElementById('base-llm');
const temperatureField = document.getElementById('temperature');
const aiKeyField = document.getElementById('ai-key');

// // Load initial config
// loadConfig();

// Handle form submission

/**
 * Fetches current configuration from the server and populates the form
 */
export async function loadMailConfig() {
    try {
        const response = await fetch('/admin/config');
        
        if (!response.ok) {
            throw new Error(`Failed to load configuration: ${response.statusText}`);
        }
        
        const config = await response.json();
        
        // Populate form fields with current values
        systemNoteField.value = config.system_note || '';
        aiEndpointField.value = config.ai_endpoint || '';
        baseLlmField.value = config.base_llm || '';
        temperatureField.value = config.temperature || 0.7;
        
        // AI key is not returned from the server for security reasons
        aiKeyField.value = '';
        
    } catch (error) {
        showToast('Error loading configuration', 'error');
        console.error('Error loading configuration:', error);
    }
}

/**
 * Handles form submission to update configuration
 * @param {Event} event - The form submission event
 */
export async function handleMailSubmit(event) {
    event.preventDefault();
    
    // Basic validation
    if (!validateForm()) {
        return;
    }
    
    const updatedConfig = {
        system_note: systemNoteField.value.trim(),
        ai_endpoint: aiEndpointField.value.trim(),
        base_llm: baseLlmField.value.trim(),
        temperature: parseFloat(temperatureField.value)
    };
    
    // Only include AI key if it was provided
    const aiKeyValue = aiKeyField.value.trim();
    if (aiKeyValue) {
        updatedConfig.ai_key = aiKeyValue;
    }
    
    try {
        const response = await fetch('/admin/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedConfig)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to update configuration: ${response.statusText}`);
        }
        
        // Clear the API key field after successful update
        aiKeyField.value = '';
        
        showToast('Configuration updated successfully', 'success');
        
    } catch (error) {
        showToast('Error updating configuration', 'error');
        console.error('Error updating configuration:', error);
    }
}

/**
 * Validates form fields before submission
 * @returns {boolean} - Whether the form is valid
 */
function validateForm() {
    // Required fields
    if (!aiEndpointField.value.trim()) {
        showToast('AI Endpoint is required', 'error');
        aiEndpointField.focus();
        return false;
    }
    
    if (!baseLlmField.value.trim()) {
        showToast('Base LLM is required', 'error');
        baseLlmField.focus();
        return false;
    }
    
    // Temperature validation (numerical between 0 and 2)
    const temperature = parseFloat(temperatureField.value);
    if (isNaN(temperature) || temperature < 0 || temperature > 2) {
        showToast('Temperature must be a number between 0 and 1', 'error');
        temperatureField.focus();
        return false;
    }
    
    return true;
}
