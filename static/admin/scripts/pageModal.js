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
    const contentTab = document.querySelector('.tab[data-tab="content"]');

    setCurrentPageId(page?.slug ?? null);

    if (page && page.slug) {
        try {
            // Fetch fresh data from the API
            const response = await fetch(`/admin/api/${page.slug}`);
            if (!response.ok) {
                throw new Error('Failed to fetch page data');
            }
            contentTab.classList.remove('disabled');
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
            renderCustomFields(freshPageData.custom || {});
        } catch (error) {
            console.error('Error fetching page data:', error);
            showToast('Failed to load page data', 'error');
            // Fall back to the original page data if available
            if (page) {
                contentTab.classList.remove('disabled');
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
                renderCustomFields({});
            }
        }
    } else {
        // Setup modal for new page
        console.log("CREATING NEW PAGE")
        contentTab.classList.add('disabled');
        document.getElementById('modal-title').textContent = 'Add New Page';
        document.getElementById('page-form').reset();
        slugInput.readOnly = false;
        setTags([]);
        setCurrentPageId(null);
        renderCustomFields({}); // Clear custom fields for new page
        // Disable edit buttons for new pages
        editWithAsta.href = '#';
        editWithAina.href = '#';
    }

    renderTags();
    // CHANGED: Switch to the 'details' tab by default instead of 'content'
    switchTab('details');
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
        html: document.getElementById('page-html').value,
        custom: collectCustomFields()
    };

    console.log(pageData)

    if (!pageData.title || !pageData.slug) {
        showToast('Title and slug are required', 'error');
        return;
    }

    fetch(currentPageId ? `/admin/api/${currentPageId}` : '/admin/api', {
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

    // --- NEW BEHAVIOR FOR EDIT BUTTONS ---
    const handleEditRedirect = (event) => {
        // 1. Stop the link from navigating immediately
        event.preventDefault();

        const destinationUrl = event.currentTarget.href;

        // 2. Do nothing if the link is disabled (e.g., for a new page)
        if (!destinationUrl || destinationUrl.endsWith('#')) {
            showToast('Please save the page first to enable the editor.', 'info');
            return;
        }

        // 3. Manually close the modal
        closePageModal();

        // 4. Navigate to the editor page after a short delay.
        // This ensures the modal is visually gone and the history state is clean.
        setTimeout(() => {
            window.location.href = destinationUrl;
        }, 150); // 150ms is enough for the modal fade-out to feel smooth
    };

    // Attach the new handler to both edit buttons
    document.getElementById('edit-with-asta').addEventListener('click', handleEditRedirect);
    document.getElementById('edit-with-aina').addEventListener('click', handleEditRedirect);
    // --- END OF NEW BEHAVIOR ---
    
    setupCustomFieldListeners();
}

// ----- Custom Fields Handling -----

function renderCustomFields(customFields = {}) {
    const container = document.getElementById('custom-fields-container');
    container.innerHTML = ''; // Clear existing

    Object.entries(customFields).forEach(([key, value]) => {
        const fieldRow = document.createElement('div');
        fieldRow.classList.add('custom-field-row');
        fieldRow.innerHTML = `
            <input type="text" class="custom-field-key form-control" value="${key}" placeholder="Field name">
            <input type="text" class="custom-field-value form-control" value="${value}" placeholder="Field value">
            <button type="button" class="btn btn-danger remove-field-btn">&times;</button>
        `;
        fieldRow.querySelector('.remove-field-btn').addEventListener('click', () => fieldRow.remove());
        container.appendChild(fieldRow);
    });
}

function collectCustomFields() {
    const container = document.getElementById('custom-fields-container');
    const rows = container.querySelectorAll('.custom-field-row');
    const fields = {};
    rows.forEach(row => {
        const key = row.querySelector('.custom-field-key').value.trim();
        const value = row.querySelector('.custom-field-value').value.trim();
        if (key) fields[key] = value;
    });
    return fields;
}

function setupCustomFieldListeners() {
    const addBtn = document.getElementById('add-custom-field-btn');
    addBtn.addEventListener('click', () => {
        const container = document.getElementById('custom-fields-container');
        const fieldRow = document.createElement('div');
        fieldRow.classList.add('custom-field-row');
        fieldRow.innerHTML = `
            <input type="text" class="custom-field-key form-control" placeholder="Field name">
            <input type="text" class="custom-field-value form-control" placeholder="Field value">
            <button type="button" class="btn btn-danger remove-field-btn">&times;</button>
        `;
        fieldRow.querySelector('.remove-field-btn').addEventListener('click', () => fieldRow.remove());
        container.appendChild(fieldRow);
    });
}