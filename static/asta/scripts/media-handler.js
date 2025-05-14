

export function setupImagePasteHandler() {
  const markdownInput = document.getElementById('markdown-input');
  
  const slug = document.getElementById('slug-container').textContent
  console.log("The current slug: "+slug)

  markdownInput.addEventListener('paste', async (event) => {
    if (event.clipboardData && event.clipboardData.items) {
      const items = event.clipboardData.items;
      
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          event.preventDefault();
          
          const file = items[i].getAsFile();
          if (!file) continue;
          
          // Sanitize the original filename to make it slug-friendly
          const originalName = file.name || 'image';
          const sanitizedName = sanitizeFilename(originalName);
          
          const timestamp = new Date().getTime();
          const filename = `${sanitizedName}-${timestamp}.png`;
          
          // Build final filename with slug if exists
          const finalFilename = slug ? `${slug}/${filename}` : filename;
          const uploadEndpoint = slug ? '/files' : '/media';

          try {
            // showNotification('Uploading image...', 'info');
            
            const formData = new FormData();
            formData.append('file', new File([file], finalFilename, { type: file.type }));
            
            const response = await fetch(uploadEndpoint, {
              method: 'POST',
              body: formData
            });
            
            if (!response.ok) {
              throw new Error('Failed to upload image');
            }
            
            const data = await response.json();
            
            const cursorPos = markdownInput.selectionStart;
            const imageMarkdown = `![${sanitizedName}](${uploadEndpoint}/${data.filename})`;
            
            const textBefore = markdownInput.value.substring(0, cursorPos);
            const textAfter = markdownInput.value.substring(cursorPos);
            markdownInput.value = textBefore + imageMarkdown + textAfter;
            
            markdownInput.selectionStart = markdownInput.selectionEnd = cursorPos + imageMarkdown.length;
            markdownInput.dispatchEvent(new Event('input'));
            
            // showNotification('Image uploaded successfully!', 'success');
          } catch (error) {
            console.error('Error uploading image:', error);
            // showNotification('Failed to upload image: ' + error.message, 'error');
          }
        }
      }
    }
  });
}

function sanitizeFilename(filename) {
  // Get the base name without extension
  const parts = filename.split('.');
  const extension = parts.length > 1 ? '.' + parts.pop() : '';
  let baseName = parts.join('.');
  
  // Convert to lowercase and replace spaces and unwanted chars with hyphens
  baseName = baseName.toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters except hyphens and underscores
    .replace(/[\s_]+/g, '-')   // Replace spaces and underscores with hyphens
    .replace(/-+/g, '-')       // Replace multiple hyphens with single hyphen
    .trim()                    // Trim whitespace from both ends
    .replace(/^-+|-+$/g, '');  // Remove leading and trailing hyphens
  
  // Limit the length of the base name (adjust as needed)
  const maxLength = 50;
  if (baseName.length > maxLength) {
    baseName = baseName.substring(0, maxLength);
  }
  
  // Ensure we have at least some filename
  if (!baseName) {
    baseName = 'image';
  }
  
  return baseName + extension;
}


  // function showNotification(message, type = 'info') {
  //   const container = document.getElementById('notification-container');
  //   const notification = document.createElement('div');
  //   notification.className = `notification ${type}`;
  //   notification.innerHTML = `
  //     <div class="notification-content">
  //       <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
  //       <span>${message}</span>
  //     </div>
  //   `;
    
  //   container.appendChild(notification);
    
  //   // Remove after 3 seconds
  //   setTimeout(() => {
  //     notification.classList.add('fade-out');
  //     setTimeout(() => {
  //       container.removeChild(notification);
  //     }, 300);
  //   }, 3000);
  // }