// pageModal.js
import { getCurrentPageId, setCurrentPageId, getTags, setTags } from './state.js';
import { switchTab } from './tabService.js';
import { fetchPages } from './pageService.js';
import { showToast } from './toastService.js';
import { renderTags } from './tagService.js';

export function openPageModal(page = null) {
    const pageModal = document.getElementById('page-modal');
    const markdownGroup = document.getElementById('markdown-group');
    const htmlGroup = document.getElementById('html-group');
    
    setCurrentPageId(page ? page.slug : null);
    
    if (page) {
        document.getElementById('modal-title').textContent = 'Edit Page';
        document.getElementById('page-title').value = page.title;
        document.getElementById('page-slug').value = page.slug;
        document.getElementById('page-description').value = page.content || '';
        document.getElementById('page-thumbnail').value = page.thumb || '';
        
        if (page.html) {
            document.getElementById('content-type').value = 'html';
            document.getElementById('page-html').value = page.html;
            markdownGroup.style.display = 'none';
            htmlGroup.style.display = 'block';
        } else {
            document.getElementById('content-type').value = 'markdown';
            document.getElementById('page-markdown').value = page.markdown || '';
            markdownGroup.style.display = 'block';
            htmlGroup.style.display = 'none';
        }
        
        setTags(page.tags || []);
        renderTags();
    } else {
        document.getElementById('modal-title').textContent = 'Add New Page';
        document.getElementById('page-form').reset();
        setTags([]);
        renderTags();
    }
    
    switchTab('content');
    pageModal.classList.add('active');
}

export function closePageModal() {
    const pageModal = document.getElementById('page-modal');
    pageModal.classList.remove('active');
}

export function savePage() {
    const currentPageId = getCurrentPageId();
    const tags = getTags();
    
    const pageData = {
        title: document.getElementById('page-title').value,
        slug: document.getElementById('page-slug').value,
        content: document.getElementById('page-description').value,
        thumb: document.getElementById('page-thumbnail').value,
        tags: tags,
    };
    
    const contentType = document.getElementById('content-type').value;
    if (contentType === 'markdown') {
        pageData.markdown = document.getElementById('page-markdown').value;
        pageData.html = null;
    } else {
        pageData.html = document.getElementById('page-html').value;
        pageData.markdown = null;
    }
    
    // Basic validation
    if (!pageData.title || !pageData.slug) {
        showToast('Title and slug are required', 'error');
        return;
    }
    
    const method = currentPageId ? 'PUT' : 'POST';
    const url = currentPageId ? `/admin/${currentPageId}` : '/admin';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(pageData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.detail || 'Failed to save page');
            });
        }
        return response.json();
    })
    .then(() => {
        showToast(`Page ${currentPageId ? 'updated' : 'created'} successfully`, 'success');
        closePageModal();
        fetchPages();
    })
    .catch(error => {
        console.error('Error saving page:', error);
        showToast(error.message, 'error');
    });
}

// Setup event listeners for modal buttons
export function setupPageModalListeners() {
    const closeModalBtn = document.getElementById('close-modal');
    const cancelBtn = document.getElementById('cancel-btn');
    const saveBtn = document.getElementById('save-btn');
    
    closeModalBtn.addEventListener('click', closePageModal);
    cancelBtn.addEventListener('click', closePageModal);
    saveBtn.addEventListener('click', savePage);
}