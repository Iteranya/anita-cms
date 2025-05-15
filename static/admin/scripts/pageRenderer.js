// pageRenderer.js
import { getPages } from './state.js';
import { openPageModal } from './pageModal.js';
import { openDeleteModal } from './deleteModal.js';
import {CONTENT_TYPES} from './pageModal.js'

export function renderPages() {
    const pages = getPages();
    const pagesTableBody = document.getElementById('pages-table-body');
    const emptyState = document.getElementById('empty-state');
    
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
        console.log("Content Of Pages: "+pages[0].type)
        typeBadge.className = 'badge ' + (page.type == CONTENT_TYPES.HTML ? 'badge-primary' : 'badge-gray');
        typeBadge.textContent = page.type == CONTENT_TYPES.HTML ? 'HTML' : 'Markdown';
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