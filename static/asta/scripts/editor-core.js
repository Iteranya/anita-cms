// editor-core.js
// Core editor functionality

import { configureMarked, initialMarkdown } from './markdown-config.js';
import {getProject} from './db-integration.js';

export class MarkdownEditor {
    constructor() {
        this.markdownInput = document.getElementById('markdown-input');
        this.markdownOutput = document.getElementById('markdown-output');
        this.side_panel =  document.getElementById('sidebar-textarea');
        this.slug = document.getElementById('slug-container').textContent;
        // Initialize with placeholder content
        console.log(this.slug)
        if (this.slug !== "" && this.slug !== null) {
            // Use await or then() since getProject returns a Promise
            getProject(this.slug)
                .then(project_data => {
                    
                    // Handle ai_notes - put in side panel if not null
                    console.log(project_data.ai_notes)
                    if (project_data.ai_notes) {
                        
                        this.side_panel.innerHTML = project_data.ai_notes;
                    }
                    
                    // Handle markdown - put in markdownInput if not null
                    console.log(project_data)
                    if (project_data.markdown) {
                        
                        this.markdownInput.value = project_data.markdown;
                    }
                    this.updatePreview();
                })
                .catch(error => {
                    console.error("Error fetching project:", error);
                    // Display error message to the user
                    this.showErrorMessage(`Failed to load project: ${error.message}`);
                });
        } else {
            this.markdownInput.value = initialMarkdown;
        }
        
        
        // Configure marked
        configureMarked();
        
        // Set up event listeners
        this.markdownInput.addEventListener('input', () => this.updatePreview());
        const modal = document.createElement('div');
        modal.className = 'rewrite-modal';
        modal.innerHTML = `
            <div class="rewrite-modal-content">
            <div class="rewrite-modal-header">
                <h4>Rewrite Selected Text</h4>
                <span class="close-modal">&times;</span>
            </div>
            <div class="rewrite-modal-body">
                <label for="rewrite-text">Rewrite:</label>
                <input type="text" id="rewrite-text" placeholder="Enter rewrite instructions">
                <button id="apply-rewrite">Apply</button>
            </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Handle right-click on markdown input
        this.markdownInput.addEventListener('contextmenu', (e) => {
            const selectedText = this.markdownInput.value.substring(
            this.markdownInput.selectionStart, 
            this.markdownInput.selectionEnd
            );

            // Only show modal if text is selected
            if (selectedText.trim().length > 0) {
            e.preventDefault(); // Prevent default context menu
            
            // Position modal near mouse
            const modalContent = modal.querySelector('.rewrite-modal-content');
            modal.style.display = 'block';
            
            // Position the modal near the cursor
            const rect = this.markdownInput.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            modalContent.style.left = `${x}px`;
            modalContent.style.top = `${y}px`;
            
            // Focus on input
            setTimeout(() => {
                document.getElementById('rewrite-text').focus();
            }, 10);
            }
        });

        // Close modal when clicking the X
        const closeModal = modal.querySelector('.close-modal');
        closeModal.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
            modal.style.display = 'none';
            }
        });

        // Handle apply button click
        const applyButton = document.getElementById('apply-rewrite');

        applyButton.addEventListener('click', async () => {
            const rewriteText = document.getElementById('rewrite-text').value;
            const selectedText = this.markdownInput.value.substring(
                this.markdownInput.selectionStart, 
                this.markdownInput.selectionEnd
            );
            
            if (rewriteText && selectedText) {
                const start = this.markdownInput.selectionStart;
                const end = this.markdownInput.selectionEnd;
                const editorContent = this.markdownInput.value;
                const sidePanelValue = this.side_panel.value;
                
                // Create and show loading overlay
                const loadingOverlay = document.createElement('div');
                loadingOverlay.className = 'loading-overlay';
                loadingOverlay.innerHTML = `<div class="loading-spinner"></div>`;
                document.body.appendChild(loadingOverlay);

                // Disable editor
                this.markdownInput.disabled = true;
                applyButton.disabled = true;
                
                try {
                    const response = await fetch('/edit-text', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            global_instruction: sidePanelValue,
                            edit_instruction: rewriteText,
                            editor_content: editorContent,
                            selected_text: selectedText
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.edited_content) {
                        const newText = data.edited_content;

                        this.markdownInput.value = 
                            this.markdownInput.value.substring(0, start) + 
                            newText + 
                            this.markdownInput.value.substring(end);

                        this.markdownInput.dispatchEvent(new Event('input'));

                        modal.style.display = 'none';
                        document.getElementById('rewrite-text').value = '';
                    } else {
                        console.error('Error: No edited content returned.', data);
                        alert('Failed to rewrite text.');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Something went wrong while rewriting.');
                } finally {
                    // Re-enable editor and remove loading overlay
                    this.markdownInput.disabled = false;
                    applyButton.disabled = false;
                    document.body.removeChild(loadingOverlay);
                }
            }
        });

        // Allow pressing Enter to apply
        document.getElementById('rewrite-text').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
            e.preventDefault();
            applyButton.click();
            }
        });
        
        // Initial rendering
        this.updatePreview();
    }
    
    updatePreview() {
        const markdownText = this.markdownInput.value;
        try {
            this.markdownOutput.innerHTML = marked.parse(markdownText);
        } catch (error) {
            console.error("Error parsing Markdown:", error);
            this.markdownOutput.innerHTML = `<p style="color: var(--accent-error);">Error parsing Markdown. Please check your syntax.</p>`;
        }
    }
    
    getValue() {
        return this.markdownInput.value;
    }
    
    setValue(value) {
        this.markdownInput.value = value;
        this.updatePreview();
    }
    
    appendValue(value) {
        this.markdownInput.value += value;
        this.updatePreview();
    }
    
    scrollToBottom() {
        this.markdownInput.scrollTop = this.markdownInput.scrollHeight;
    }
}

export function toggleSidebar() {
    const isCollapsed = sidebar.classList.toggle('collapsed');
    const sidebarToggle = document.getElementById('sidebar-toggle')
    
    const mainContent = document.getElementById('main-content');
    mainContent.classList.toggle('sidebar-collapsed', isCollapsed);

    // Update toggle button icon
    const icon = sidebarToggle.querySelector('i');
    if (isCollapsed) {
        icon.classList.remove('fa-chevron-left');
        icon.classList.add('fa-chevron-right');
        sidebarToggle.setAttribute('aria-label', 'Expand Sidebar');
    } else {
        icon.classList.remove('fa-chevron-right');
        icon.classList.add('fa-chevron-left');
        sidebarToggle.setAttribute('aria-label', 'Collapse Sidebar');
    }
}