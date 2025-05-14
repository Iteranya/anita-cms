// tabService.js
export function switchTab(tabName) {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
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

export function updatePreview() {
    const contentType = document.getElementById('content-type').value;
    const previewContent = document.getElementById('preview-content');
    let previewText = '';
    
    if (contentType === 'markdown') {
        previewText = document.getElementById('page-markdown').value || 'No markdown content to preview';
    } else {
        previewText = document.getElementById('page-html').value || 'No HTML content to preview';
    }
    
    previewContent.innerHTML = previewText;
}