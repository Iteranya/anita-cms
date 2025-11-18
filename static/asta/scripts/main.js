// main.js
// Main entry point that initializes all modules

import { MarkdownEditor, toggleSidebar } from './editor-core.js';
import { NotificationSystem } from './notification-system.js';
import { getProject } from './db-integration.js'; // Make sure this is imported
import { initialMarkdown } from './markdown-config.js'; // Import the default text
import { setupImagePasteHandler } from './media-handler.js';
import { ButtonHandlers } from './button-handler.js';
import { AiGenerator } from './ai-integration.js'; 
// Use an async function to allow 'await' for data fetching
document.addEventListener('DOMContentLoaded', async () => {
    // --- 1. GET UI ELEMENTS AND SLUG ---
    const inputElement = document.getElementById('markdown-input');
    const outputElement = document.getElementById('markdown-output');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidePanel = document.getElementById('sidebar-textarea');
    const slug = document.getElementById('slug-container').textContent.trim();
    
    // --- 2. FETCH DATA ONCE ---
    // Define a default project structure for new projects
    let projectData = {
        markdown: initialMarkdown,
        ai_notes: '',
        tags: []
    };

    if (slug) {
        try {
            // This is now the ONLY place we call getProject
            console.log(`Fetching project data for slug: ${slug}`);
            projectData = await getProject(slug);
        } catch (error) {
            console.error("Failed to fetch project data in main.js:", error);
            NotificationSystem.show(`Error loading project: ${error.message}`, 'error');
            // We can continue with the default empty projectData
        }
    }

    // --- 3. INITIALIZE MODULES AND PASS DATA TO THEM ---
    setupImagePasteHandler();

    // Initialize the editor and pass the relevant data to it
    const editor = new MarkdownEditor(projectData);
    
    // Initialize buttons and pass the relevant data to them
    initializeButtons(slug, inputElement, sidePanel, projectData);

    // Initialize AI generation (if it needs data, pass it here too)
    const aiGenerator = new AiGenerator(editor); 
    
    sidebarToggle.addEventListener('click', toggleSidebar);
    
    console.log('Application initialized successfully with project data.');
});

// --- NO CHANGES NEEDED BELOW THIS LINE for main.js ---
// This function now receives the full projectData object
function initializeButtons(slug, inputElement, sidePanel, projectData) {
    const actionButton = document.getElementById('action-button');
    const blogToggle = document.getElementById('blog-toggle-checkbox');
    
    const initialTags = projectData.tags || [];

    // Set initial toggle state from our single source of truth
    if (blogToggle) {
        const hasBlogTag = Array.isArray(initialTags) && initialTags.includes('blog');
        blogToggle.checked = hasBlogTag;
    }

    // Set up the click handler
    if (actionButton) {
        if (!slug) {
            actionButton.style.display = 'none';
        } else {
            actionButton.addEventListener('click', () => {
                const isBlog = blogToggle.checked;
                
                // IMPORTANT: Always start modifications from the original data
                let project_tags = [...initialTags];
                const hasBlogTag = project_tags.includes('blog');

                if (isBlog && !hasBlogTag) {
                    project_tags.push('blog');
                } else if (!isBlog && hasBlogTag) {
                    project_tags = project_tags.filter(tag => tag !== 'blog');
                }

                ButtonHandlers.handleActionButton(
                    slug,
                    inputElement.value,
                    sidePanel.value,
                    project_tags,
                    isBlog
                );
            });
        }
    }
}