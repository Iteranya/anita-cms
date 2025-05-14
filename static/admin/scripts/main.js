// main.js
import { openPageModal } from './pageModal.js';
import { filterPages } from './pageService.js';
import { switchTab } from './tabService.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const addPageBtn = document.getElementById('add-page-btn');
    const emptyAddBtn = document.getElementById('empty-add-btn');
    const searchInput = document.getElementById('search-input');
    const contentTypeSelect = document.getElementById('content-type');
    const markdownGroup = document.getElementById('markdown-group');
    const htmlGroup = document.getElementById('html-group');
    
    // Event Listeners
    addPageBtn?.addEventListener('click', () => openPageModal());
    emptyAddBtn?.addEventListener('click', () => openPageModal());
    searchInput?.addEventListener('input', () => filterPages());
    
    // Content type switching
    contentTypeSelect?.addEventListener('change', () => {
        const contentType = contentTypeSelect.value;
        if (contentType === 'markdown') {
            markdownGroup.style.display = 'block';
            htmlGroup.style.display = 'none';
        } else {
            markdownGroup.style.display = 'none';
            htmlGroup.style.display = 'block';
        }
    });

    // Setup tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
});