// tagService.js
import { getTags, addTag, removeTag } from './state.js';

export function renderTags() {
    const tags = getTags();
    const tagsContainer = document.getElementById('tags-container');
    const tagsInput = document.getElementById('page-tags-input');
    
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
            removeTag(tagToRemove);
            renderTags();
        });
    });
}

export function setupTagInputListener() {
    const tagsInput = document.getElementById('page-tags-input');
    
    tagsInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const tag = tagsInput.value.trim();
            if (addTag(tag)) {
                renderTags();
                tagsInput.value = '';
            }
        }
    });
}