import { showToast } from './toastService.js';

// Get form references
const serverEmailField = document.getElementById('server-email');
const targetEmailField = document.getElementById('target-email');
const headerField = document.getElementById('header');
const footerField = document.getElementById('footer');
const apiKeyField = document.getElementById('api-key'); // Matches the HTML id="api-key"

/**
 * Fetches current mail configuration from the server and populates the form.
 */
export async function loadMailConfig() {
    try {
        const response = await fetch('/admin/mail'); // Updated endpoint to match Python router @router.get("/mail",...)

        if (!response.ok) {
            throw new Error(`Failed to load mail configuration: ${response.statusText}`);
        }

        const config = await response.json();

        // Populate form fields with current values
        serverEmailField.value = config.server_email || 'onboarding@resend.dev'; // Default as per HTML
        targetEmailField.value = config.target_email || '';
        headerField.value = config.header || '';
        footerField.value = config.footer || ''; // Python returns config.header for footer, assuming typo and should be config.footer

        // API key is not returned from the server for security reasons (as per Python GET endpoint)
        apiKeyField.value = '';

    } catch (error) {
        showToast('Error loading mail configuration', 'error');
        console.error('Error loading mail configuration:', error);
    }
}

/**
 * Handles form submission to update mail configuration.
 * @param {Event} event - The form submission event.
 */
export async function handleMailSubmit(event) {
    event.preventDefault();

    // Basic validation
    if (!validateMailForm()) { // Renamed for clarity if you have other forms
        return;
    }

    const updatedConfig = {
        server_email: serverEmailField.value.trim(),
        target_email: targetEmailField.value.trim(),
        header: headerField.value.trim(),
        footer: footerField.value.trim(),
        // api_key is handled separately below as it's sensitive and might not always be updated
    };

    // Only include API key if it was provided
    const apiKeyValue = apiKeyField.value.trim(); // Does not use .trim() for API keys usually. Reverted.
    if (apiKeyField.value) { // Check if the field has a value, no .trim() for API keys
        updatedConfig.api_key = apiKeyField.value; // Matches MailModel: api_key
    } else {
        updatedConfig.api_key = null; // Explicitly send empty string if field is empty to clear it
    }


    try {
        const response = await fetch('/admin/mail', { // Updated endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedConfig)
        });

        if (!response.ok) {
             const errorData = await response.json().catch(() => ({ detail: `Failed to update mail configuration: ${response.statusText}` }));
            throw new Error(errorData.detail || `Failed to update mail configuration: ${response.statusText}`);
        }

        // Clear the API key field after successful update for security
        apiKeyField.value = '';

        showToast('Mail configuration updated successfully', 'success');

    } catch (error) {
        showToast(error.message || 'Error updating mail configuration', 'error');
        console.error('Error updating mail configuration:', error);
    }
}

/**
 * Validates mail form fields before submission.
 * @returns {boolean} - Whether the form is valid.
 */
function validateMailForm() { // Renamed for clarity
    // Required fields validation (example)
    if (!serverEmailField.value.trim()) {
        showToast('Server Email is required', 'error');
        serverEmailField.focus();
        return false;
    }
    if (!targetEmailField.value.trim()) {
        showToast('Target Email is required', 'error');
        targetEmailField.focus();
        return false;
    }

    // Email format validation (basic example)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(serverEmailField.value.trim())) {
        showToast('Invalid Server Email format', 'error');
        serverEmailField.focus();
        return false;
    }
    if (targetEmailField.value.trim() && !emailRegex.test(targetEmailField.value.trim())) {
        // targetEmailField might be optional, so only validate if not empty
        showToast('Invalid Target Email format', 'error');
        targetEmailField.focus();
        return false;
    }

    return true;
}