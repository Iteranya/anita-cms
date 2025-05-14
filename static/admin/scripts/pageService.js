// pageService.js
import { setPages, getPages } from './state.js';
import { renderPages } from './pageRenderer.js';
import { showToast } from './toastService.js';

export function fetchPages() {
    fetch('/admin/list')
        .then(response => response.json())
        .then(data => {
            setPages(data);
            renderPages();
        })
        .catch(error => {
            console.error('Error fetching pages:', error);
            showToast('Failed to load pages', 'error');
        });
}

export function filterPages() {
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.toLowerCase();
    const pages = getPages();
    const emptyState = document.getElementById('empty-state');
    
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