// main.js
import { openPageModal } from './pageModal.js';
import { filterPages } from './pageService.js';
import { switchTab } from './tabService.js';
import {loadConfig,handleSubmit} from './config.js'
import {loadMailConfig,handleMailSubmit} from './mail.js'

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const addPageBtn = document.getElementById('add-page-btn');
    const emptyAddBtn = document.getElementById('empty-add-btn');
    const searchInput = document.getElementById('search-input');
    const contentTypeSelect = document.getElementById('content-type');
    const markdownGroup = document.getElementById('markdown-group');
    const htmlGroup = document.getElementById('html-group');
    const editWithAsta = document.getElementById('edit-with-asta');
    const editWithAina = document.getElementById('edit-with-aina');
    const slugInput = document.getElementById('page-slug');
    const pagesPanel = document.getElementById('pages-panel');
    const configPanel = document.getElementById('config-panel');
    const mailPanel = document.getElementById('mail-panel');
    const pagesLink = document.getElementById('pages-link');
    const configLink = document.getElementById('config-link');
    const configForm = document.getElementById('config-form');
    const mailLink = document.getElementById('mail-link');
    const mailForm = document.getElementById('mail-form');

    // Event Listeners
    addPageBtn?.addEventListener('click', () => openPageModal());
    emptyAddBtn?.addEventListener('click', () => openPageModal());
    searchInput?.addEventListener('input', () => filterPages());
    configForm.addEventListener('submit', handleSubmit);
    mailForm.addEventListener('submit', handleMailSubmit);

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

     // Get panel elements

    // Handle panel switching
    pagesLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Update active link
        pagesLink.classList.add('active');
        configLink.classList.remove('active');
        mailLink.classList.remove('active');
        
        // Show pages panel, hide config panel
        pagesPanel.classList.add('active-panel');
        configPanel.classList.remove('active-panel');
        mailPanel.classList.remove('active-panel');
    });
    
    configLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Update active link
        configLink.classList.add('active');
        pagesLink.classList.remove('active');
        mailLink.classList.remove('active');
        
        // Show config panel, hide pages panel
        configPanel.classList.add('active-panel');
        pagesPanel.classList.remove('active-panel');
        mailPanel.classList.remove('active-panel');
    });

    mailLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Update active link
        configLink.classList.remove('active');
        pagesLink.classList.remove('active');
        mailLink.classList.add('active');
        
        // Show config panel, hide pages panel
        configPanel.classList.remove('active-panel');
        pagesPanel.classList.remove('active-panel');
        mailPanel.classList.add('active-panel');
    });
    
    // Initialize - show pages panel by default
    pagesPanel.classList.add('active-panel');
    configPanel.classList.remove('active-panel');
    mailPanel.classList.remove('active-panel');

     // Function to update button links with the current slug value
    function updateEditLinks() {
        const currentSlug = slugInput.value || '';
        editWithAsta.href = `/asta?slug=${currentSlug}`;
        editWithAina.href = `/aina?slug=${currentSlug}`;
    }
    
    // Update links when slug changes
    slugInput.addEventListener('input', updateEditLinks);
    
    // Update links when form loads or modal opens
    function initialLinkSetup() {
        updateEditLinks();
    }
    loadConfig();
    loadMailConfig();
    initialLinkSetup();
});