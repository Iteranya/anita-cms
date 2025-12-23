// fileHandler.js - File import/export functionality
import { showNotification } from './notifications.js';

/**
 * Set up file handling functionality (import/export)
 * @param {HTMLTextAreaElement} htmlCode - The HTML editor element
 * @param {Function} updatePreviewCallback - Callback to update the preview
 */
export function setupFileHandlers(htmlCode, updatePreviewCallback) {
    // Get references to the buttons
    const exportBtn = document.getElementById('export-btn');
    const importBtn = document.getElementById('import-btn');

    // Export functionality
    exportBtn.addEventListener('click', function() {
        // Get the HTML content from the textarea
        const content = htmlCode.value;
        
        // Create a Blob with the HTML content
        const blob = new Blob([content], { type: 'text/html' });
        
        // Create a temporary URL for the Blob
        const url = URL.createObjectURL(blob);
        
        // Create a temporary link element to trigger the download
        const a = document.createElement('a');
        a.href = url;
        a.download = 'my-webpage.html'; // Default filename
        
        // Append the link to the body (not visible)
        document.body.appendChild(a);
        
        // Programmatically click the link to trigger download
        a.click();
        
        // Clean up by removing the link and revoking the URL
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Show a notification to confirm export
        showNotification('HTML file downloaded successfully! ✨', 'success');
    });

    // Import functionality
    importBtn.addEventListener('click', function() {
        // Create a file input element
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.html,.htm';
        
        // Add change event handler to the file input
        fileInput.addEventListener('change', function(e) {
            // Get the selected file
            const file = e.target.files[0];
            
            if (file) {
                // Create a FileReader to read the file contents
                const reader = new FileReader();
                
                // Add load event handler to the reader
                reader.addEventListener('load', function() {
                    // Set the content of the textarea to the file contents
                    htmlCode.value = reader.result;
                    
                    // Update the preview
                    updatePreviewCallback(htmlCode, document.getElementById('preview'));
                    
                    // Show a notification to confirm import
                    showNotification('HTML file imported successfully! ✨', 'success');
                });
                
                // Read the file as text
                reader.readAsText(file);
            }
        });
        
        // Programmatically click the file input to open the file selection dialog
        fileInput.click();
    });
}