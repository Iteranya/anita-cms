import { getCurrentPageId, setCurrentPageId, getTags, setTags } from './state.js';
import { switchTab } from './tabService.js';
import { fetchPages } from './pageService.js';
import { showToast } from './toastService.js';
import { renderTags } from './tagService.js';

export const CONTENT_TYPES = {
    MARKDOWN: 'markdown',
    HTML: 'html'
};

export async function openPageModal(page = null) {
    const pageModal = document.getElementById('page-modal');
    const markdownGroup = document.getElementById('markdown-group');
    const htmlGroup = document.getElementById('html-group');
    const slugInput = document.getElementById('page-slug');
    const editWithAsta = document.getElementById('edit-with-asta');
    const editWithAina = document.getElementById('edit-with-aina');
    
    setCurrentPageId(page?.slug ?? null);
    
    if (page) {
        try {
            // Fetch fresh data from the API
            const response = await fetch(`/admin/${page.slug}`);
            if (!response.ok) {
                throw new Error('Failed to fetch page data');
            }
            const freshPageData = await response.json();
            
            // Setup modal with fresh data
            document.getElementById('modal-title').textContent = 'Edit Page';
            document.getElementById('page-title').value = freshPageData.title;
            slugInput.value = freshPageData.slug;
            slugInput.readOnly = true;
            document.getElementById('page-description').value = freshPageData.content || '';
            document.getElementById('page-thumbnail').value = freshPageData.thumb || '';
            
            // Populate content fields
            document.getElementById('page-markdown').value = freshPageData.markdown || '';
            document.getElementById('page-html').value = freshPageData.html || '';
            
            // Set content type (default to markdown if not specified)
            const contentType = freshPageData.type || CONTENT_TYPES.MARKDOWN;
            document.getElementById('content-type').value = contentType;
            
            // Update editor visibility based on content type
            updateContentVisibility(contentType);
            
            // Update editor links
            editWithAsta.href = `/asta?slug=${freshPageData.slug}`;
            editWithAina.href = `/aina?slug=${freshPageData.slug}`;
            
            setTags(freshPageData.tags || []);
        } catch (error) {
            console.error('Error fetching page data:', error);
            showToast('Failed to load page data', 'error');
            // Fall back to the original page data if available
            if (page) {
                document.getElementById('modal-title').textContent = 'Edit Page';
                document.getElementById('page-title').value = page.title;
                slugInput.value = page.slug;
                slugInput.readOnly = true;
                document.getElementById('page-description').value = page.content || '';
                document.getElementById('page-thumbnail').value = page.thumb || '';
                document.getElementById('page-markdown').value = page.markdown || '';
                document.getElementById('page-html').value = page.html || '';
                const contentType = page.type || CONTENT_TYPES.MARKDOWN;
                document.getElementById('content-type').value = contentType;
                updateContentVisibility(contentType);
                editWithAsta.href = `/asta?slug=${page.slug}`;
                editWithAina.href = `/aina?slug=${page.slug}`;
                setTags(page.tags || []);
            }
        }
    } else {
        // Setup modal for new page
        document.getElementById('modal-title').textContent = 'Add New Page';
        document.getElementById('page-form').reset();
        slugInput.readOnly = false;
        setTags([]);
        
        // Disable edit buttons for new pages
        editWithAsta.href = '#';
        editWithAina.href = '#';
    }
    
    renderTags();
    switchTab('content');
    pageModal.classList.add('active');
}

function updateContentVisibility(contentType) {
    const markdownGroup = document.getElementById('markdown-group');
    const htmlGroup = document.getElementById('html-group');
    
    markdownGroup.style.display = contentType === CONTENT_TYPES.MARKDOWN ? 'block' : 'none';
    htmlGroup.style.display = contentType === CONTENT_TYPES.HTML ? 'block' : 'none';
}

export function closePageModal() {
    document.getElementById('page-modal').classList.remove('active');
}

export function updateEditorLinks() {
    const slug = document.getElementById('page-slug').value;
    document.getElementById('edit-with-asta').href = `/asta?slug=${slug}`;
    document.getElementById('edit-with-aina').href = `/aina?slug=${slug}`;
}

export function savePage() {
    const currentPageId = getCurrentPageId();
    const contentType = document.getElementById('content-type').value;
    
    const pageData = {
        title: document.getElementById('page-title').value,
        slug: document.getElementById('page-slug').value,
        content: document.getElementById('page-description').value,
        thumb: document.getElementById('page-thumbnail').value,
        tags: getTags(),
        type: contentType,
        // Always include both content types, but only one will be "active"
        markdown: document.getElementById('page-markdown').value,
        html: document.getElementById('page-html').value
    };

    console.log(pageData)
    
    if (!pageData.title || !pageData.slug) {
        showToast('Title and slug are required', 'error');
        return;
    }
    
    fetch(currentPageId ? `/admin/${currentPageId}` : '/admin', {
        method: currentPageId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pageData)
    })
    .then(handleResponse)
    .then(() => {
        showToast(`Page ${currentPageId ? 'updated' : 'created'} successfully`, 'success');
        closePageModal();
        fetchPages();
    })
    .catch(handleError);
}

function handleResponse(response) {
    if (!response.ok) {
        return response.json().then(err => {
            throw new Error(err.detail || 'Failed to save page');
        });
    }
    return response.json();
}

function handleError(error) {
    console.error('Error saving page:', error);
    showToast(error.message, 'error');
}

export function setupPageModalListeners() {
    document.getElementById('close-modal').addEventListener('click', closePageModal);
    document.getElementById('cancel-btn').addEventListener('click', closePageModal);
    document.getElementById('save-btn').addEventListener('click', savePage);
    
    document.getElementById('content-type').addEventListener('change', (e) => {
        updateContentVisibility(e.target.value);
    });
    
    document.getElementById('page-slug').addEventListener('input', updateEditorLinks);
}