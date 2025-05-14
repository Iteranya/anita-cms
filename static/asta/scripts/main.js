// main.js
// Main entry point that initializes all modules

import { MarkdownEditor, toggleSidebar } from './editor-core.js';
import { NotificationSystem } from './notification-system.js';
import { ScrollSynchronizer } from './scroll-sync.js';
import { AiGenerator } from './ai-integration.js';
import { setupImagePasteHandler } from './media-handler.js';
import { ButtonHandlers } from './button-handler.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the editor
    const editor = new MarkdownEditor();
    
    // Initialize scroll synchronization
    const inputElement = document.getElementById('markdown-input');
    const outputElement = document.getElementById('markdown-output');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const side_panel = document.getElementById('sidebar-textarea');
    const slug = document.getElementById('slug-container').textContent;
    
    setupImagePasteHandler();

    // Initialize buttons
    initializeButtons(slug, inputElement, side_panel);

    // Initialize AI generation
    const aiGenerator = new AiGenerator(editor);
    sidebarToggle.addEventListener('click', toggleSidebar);
    console.log('Markdown editor initialized successfully!');
});

function initializeButtons(slug, inputElement, sidePanel) {
    const actionButton = document.getElementById('action-button');
    const projectButton = document.getElementById('project-button');
    const latexButton = document.getElementById('latex-button');

    // Handle action button
    if (actionButton) {
        
        if (slug == null || slug == "") {
            actionButton.style.display = 'none';
            projectButton.style.display = 'none';
            latexButton.style.display = 'none';
        } else {
            actionButton.addEventListener('click', () => 
                ButtonHandlers.handleActionButton(slug, inputElement.value, sidePanel.value)
            );
        }
    }

    // Handle project button
    if (projectButton) {
        projectButton.addEventListener('click', () => 
            ButtonHandlers.handleProjectButton(slug, inputElement.value, sidePanel.value)
        );
    }

    // Handle latex button
    if (latexButton) {
        latexButton.addEventListener('click', () => 
            ButtonHandlers.handleLatexButton(slug, inputElement.value, sidePanel.value)
        );
    }
}