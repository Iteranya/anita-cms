// deleteModal.js
import { setCurrentPageId, getCurrentPageId } from './state.js';
import { fetchPages } from './pageService.js';
import { showToast } from './toastService.js';

export function openDeleteModal(slug) {
    const deleteModal = document.getElementById('delete-modal');
    setCurrentPageId(slug);
    deleteModal.classList.add('active');
}

export function closeDeleteModal() {
    const deleteModal = document.getElementById('delete-modal');
    deleteModal.classList.remove('active');
}

export function deletePage() {
    const currentPageId = getCurrentPageId();
    
    fetch(`/admin/api/${currentPageId}`, {
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

// Setup event listeners for delete modal
export function setupDeleteModalListeners() {
    const closeDeleteModalBtn = document.getElementById('close-delete-modal');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    
    closeDeleteModalBtn.addEventListener('click', closeDeleteModal);
    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    confirmDeleteBtn.addEventListener('click', deletePage);
}