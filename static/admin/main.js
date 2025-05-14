document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const addPageBtn = document.getElementById('add-page-btn');
    const emptyAddBtn = document.getElementById('empty-add-btn');
    const pageModal = document.getElementById('page-modal');
    const deleteModal = document.getElementById('delete-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const closeDeleteModalBtn = document.getElementById('close-delete-modal');
    const cancelBtn = document.getElementById('cancel-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const saveBtn = document.getElementById('save-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const pageForm = document.getElementById('page-form');
    const pagesTableBody = document.getElementById('pages-table-body');
    const emptyState = document.getElementById('empty-state');
    const searchInput = document.getElementById('search-input');
    const toast = document.getElementById('toast');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const contentTypeSelect = document.getElementById('content-type');
    const markdownGroup = document.getElementById('markdown-group');
    const htmlGroup = document.getElementById('html-group');
    const previewContent = document.getElementById('preview-content');
    
    // State
    let currentPageId = null;
    let pages = [];
    let tags = [];
    
    // Initialize
    fetchPages();
    
    // Event Listeners
    addPageBtn.addEventListener('click', () => openPageModal());
    emptyAddBtn.addEventListener('click', () => openPageModal());
    closeModalBtn.addEventListener('click', () => closePageModal());
    closeDeleteModalBtn.addEventListener('click', () => closeDeleteModal());
    cancelBtn.addEventListener('click', () => closePageModal());
    cancelDeleteBtn.addEventListener('click', () => closeDeleteModal());
    saveBtn.addEventListener('click', () => savePage());
    confirmDeleteBtn.addEventListener('click', () => deletePage());
    searchInput.addEventListener('input', () => filterPages());
    
    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Content type switching
    contentTypeSelect.addEventListener('change', () => {
        const contentType = contentTypeSelect.value;
        if (contentType === 'markdown') {
            markdownGroup.style.display = 'block';
            htmlGroup.style.display = 'none';
        } else {
            markdownGroup.style.display = 'none';
            htmlGroup.style.display = 'block';
        }
    });
    
    // Tags input
    const tagsContainer = document.getElementById('tags-container');
    const tagsInput = document.getElementById('page-tags-input');
    
    tagsInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const tag = tagsInput.value.trim();
            if (tag && !tags.includes(tag)) {
                tags.push(tag);
                renderTags();
                tagsInput.value = '';
            }
        }
    });
    
    // Functions
    function fetchPages() {
        fetch('/admin/list')
            .then(response => response.json())
            .then(data => {
                pages = data;
                renderPages();
            })
            .catch(error => {
                console.error('Error fetching pages:', error);
                showToast('Failed to load pages', 'error');
            });
    }
    
    function renderPages() {
        if (pages.length === 0) {
            emptyState.style.display = 'block';
            document.getElementById('pages-table').style.display = 'none';
            return;
        }
        
        emptyState.style.display = 'none';
        document.getElementById('pages-table').style.display = 'table';
        
        pagesTableBody.innerHTML = '';
        
        pages.forEach(page => {
            const row = document.createElement('tr');
            
            // Title
            const titleCell = document.createElement('td');
            titleCell.textContent = page.title;
            row.appendChild(titleCell);
            
            // Slug
            const slugCell = document.createElement('td');
            slugCell.textContent = page.slug;
            row.appendChild(slugCell);
            
            // Content Type
            const typeCell = document.createElement('td');
            const typeBadge = document.createElement('span');
            typeBadge.className = 'badge ' + (page.html ? 'badge-primary' : 'badge-gray');
            typeBadge.textContent = page.html ? 'HTML' : 'Markdown';
            typeCell.appendChild(typeBadge);
            row.appendChild(typeCell);
            
            // Tags
            const tagsCell = document.createElement('td');
            if (page.tags && page.tags.length > 0) {
                const tagsContainer = document.createElement('div');
                tagsContainer.style.display = 'flex';
                tagsContainer.style.gap = '0.25rem';
                tagsContainer.style.flexWrap = 'wrap';
                
                page.tags.slice(0, 3).forEach(tag => {
                    const tagElement = document.createElement('span');
                    tagElement.className = 'badge badge-gray';
                    tagElement.textContent = tag;
                    tagsContainer.appendChild(tagElement);
                });
                
                if (page.tags.length > 3) {
                    const moreBadge = document.createElement('span');
                    moreBadge.className = 'badge badge-gray';
                    moreBadge.textContent = `+${page.tags.length - 3}`;
                    tagsContainer.appendChild(moreBadge);
                }
                
                tagsCell.appendChild(tagsContainer);
            } else {
                tagsCell.textContent = 'No tags';
            }
            row.appendChild(tagsCell);
            
            // Actions
            const actionsCell = document.createElement('td');
            const actionsContainer = document.createElement('div');
            actionsContainer.className = 'actions';
            
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-outline';
            editBtn.innerHTML = '<i class="fas fa-edit"></i>';
            editBtn.title = 'Edit';
            editBtn.addEventListener('click', () => openPageModal(page));
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-outline';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.title = 'Delete';
            deleteBtn.addEventListener('click', () => openDeleteModal(page.slug));
            
            actionsContainer.appendChild(editBtn);
            actionsContainer.appendChild(deleteBtn);
            actionsCell.appendChild(actionsContainer);
            row.appendChild(actionsCell);
            
            pagesTableBody.appendChild(row);
        });
    }
    
    function filterPages() {
        const searchTerm = searchInput.value.toLowerCase();
        if (!searchTerm) {
            renderPages();
            return;
        }
        
        const filteredPages = pages.filter(page => 
            page.title.toLowerCase().includes(searchTerm) || 
            page.slug.toLowerCase().includes(searchTerm) ||
            (page.tags && page.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
        );
        
        if (filteredPages.length === 0) {
            emptyState.style.display = 'block';
            document.getElementById('pages-table').style.display = 'none';
            return;
        }
        
        emptyState.style.display = 'none';
        document.getElementById('pages-table').style.display = 'table';
        
        const rows = document.querySelectorAll('#pages-table-body tr');
        rows.forEach(row => {
            const title = row.cells[0].textContent.toLowerCase();
            const slug = row.cells[1].textContent.toLowerCase();
            const tagsText = row.cells[3].textContent.toLowerCase();
            
            if (title.includes(searchTerm) || slug.includes(searchTerm) || tagsText.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    function openPageModal(page = null) {
        currentPageId = page ? page.slug : null;
        
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
            
            tags = page.tags || [];
            renderTags();
        } else {
            document.getElementById('modal-title').textContent = 'Add New Page';
            document.getElementById('page-form').reset();
            tags = [];
            renderTags();
        }
        
        switchTab('content');
        pageModal.classList.add('active');
    }
    
    function closePageModal() {
        pageModal.classList.remove('active');
    }
    
    function openDeleteModal(slug) {
        currentPageId = slug;
        deleteModal.classList.add('active');
    }
    
    function closeDeleteModal() {
        deleteModal.classList.remove('active');
    }
    
    function switchTab(tabName) {
        // Update active tab
        tabs.forEach(tab => {
            if (tab.getAttribute('data-tab') === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update active content
        tabContents.forEach(content => {
            if (content.getAttribute('data-tab-content') === tabName) {
                content.classList.add('active');
                
                // If switching to preview tab, update the preview
                if (tabName === 'preview') {
                    updatePreview();
                }
            } else {
                content.classList.remove('active');
            }
        });
    }
    
    function updatePreview() {
        const contentType = document.getElementById('content-type').value;
        let previewText = '';
        
        if (contentType === 'markdown') {
            previewText = document.getElementById('page-markdown').value || 'No markdown content to preview';
        } else {
            previewText = document.getElementById('page-html').value || 'No HTML content to preview';
        }
        
        previewContent.innerHTML = previewText;
    }
    
    function renderTags() {
        tagsContainer.innerHTML = '';
        
        tags.forEach(tag => {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag';
            tagElement.innerHTML = `
                <span>${tag}</span>
                <span class="tag-remove" data-tag="${tag}">&times;</span>
            `;
            tagsContainer.appendChild(tagElement);
        });
        
        // Add the input at the end
        tagsContainer.appendChild(tagsInput);
        
        // Add event listeners to remove buttons
        document.querySelectorAll('.tag-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tagToRemove = e.target.getAttribute('data-tag');
                tags = tags.filter(t => t !== tagToRemove);
                renderTags();
            });
        });
    }
    
    function savePage() {
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
    
    function deletePage() {
        fetch(`/admin/${currentPageId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete page');
            }
            return response.json();
        })
        .then(() => {
            showToast('Page deleted successfully', 'success');
            closeDeleteModal();
            fetchPages();
        })
        .catch(error => {
            console.error('Error deleting page:', error);
            showToast('Failed to delete page', 'error');
        });
    }
    
    function showToast(message, type = 'info') {
        toast.textContent = message;
        toast.className = 'toast';
        toast.classList.add(`toast-${type}`);
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});