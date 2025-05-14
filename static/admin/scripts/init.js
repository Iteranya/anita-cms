// init.js
import { fetchPages } from './pageService.js';
import { setupPageModalListeners } from './pageModal.js';
import { setupDeleteModalListeners } from './deleteModal.js';
import { setupTagInputListener } from './tagService.js';

export function initializeApp() {
    // Set up all event listeners
    setupPageModalListeners();
    setupDeleteModalListeners();
    setupTagInputListener();
    
    // Initial data load
    fetchPages();
}