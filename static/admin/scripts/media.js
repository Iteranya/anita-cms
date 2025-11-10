// media.js
import { showToast } from './toastService.js';

const API = '/media';

let panel, grid, empty, fileIn, filterInput, uploadBtn, emptyUploadBtn, modal, modalImg, modalCaption, modalOpenLink;
let lastImages = [];
let initialized = false;

function initOnce() {
  if (initialized) return;

  panel = document.getElementById('media-panel');
  if (!panel) return; // panel not in DOM yet

  // Scope to the media panel to avoid ID collisions elsewhere
  grid           = panel.querySelector('#gallery-grid');
  empty          = panel.querySelector('#empty-state');       // scoped!
  fileIn         = panel.querySelector('#file-picker');
  filterInput    = panel.querySelector('#filter-input');
  uploadBtn      = panel.querySelector('#upload-btn');
  emptyUploadBtn = panel.querySelector('#empty-upload-btn');

  // Modal might be inside the panel; fallback to document if you mounted it globally
  modal          = panel.querySelector('#media-modal') || document.getElementById('media-modal');
  modalImg       = panel.querySelector('#media-modal-img') || document.getElementById('media-modal-img');
  modalCaption   = panel.querySelector('#media-modal-caption') || document.getElementById('media-modal-caption');
  modalOpenLink  = panel.querySelector('#media-modal-open') || document.getElementById('media-modal-open');

  if (!grid) return;

  // Grid actions: open, delete, copy
  grid.addEventListener('click', async (e) => {
    const del  = e.target.closest('.btn-delete');
    const copy = e.target.closest('.btn-copy');
    const img  = e.target.closest('img');

    if (del) {
      const name = del.dataset.name;
      if (!confirm(`Delete ${name}?`)) return;
      try {
        const res = await fetch(`${API}/${encodeURIComponent(name)}`, { method: 'DELETE' });
        if (!res.ok) throw new Error(await res.text());
        showToast('Image deleted', 'success');
        await refreshMediaPage();
      } catch {
        showToast('Delete failed', 'error');
      }
      return;
    }

    if (copy) {
      const name = copy.dataset.name;
      const url = `${API}/${encodeURIComponent(name)}`;
      try {
        if (navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(url);
        } else {
          const ta = document.createElement('textarea');
          ta.value = url;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
        }
        showToast('Image URL copied', 'success');
      } catch {
        showToast('Copy failed', 'error');
      }
      return;
    }

    if (img && img.dataset.name) {
      openModal(img.src, img.dataset.name);
    }
  });

  // Upload
  function openPicker() { fileIn?.click(); }
  uploadBtn     ?.addEventListener('click', openPicker);
  emptyUploadBtn?.addEventListener('click', openPicker);

fileIn?.addEventListener('change', async () => {
    if (!fileIn.files.length) return; // Changed from files[0] to files.length
    
    const fd = new FormData();
    
    // Append ALL selected files with the same key name
    for (let i = 0; i < fileIn.files.length; i++) {
      fd.append('files', fileIn.files[i]); // Changed 'file' to 'files'
    }
    
    try {
      const res = await fetch(API, { method: 'POST', body: fd });
      if (!res.ok) throw new Error(await res.text());
      showToast(`${fileIn.files.length} image(s) uploaded`, 'success'); // Better feedback
      fileIn.value = '';
      await refreshMediaPage();
    } catch {
      showToast('Upload failed', 'error');
    }
});

  // Filter (client-side)
  filterInput?.addEventListener('input', () => {
    const q = (filterInput.value || '').toLowerCase();
    const filtered = lastImages.filter(n => n.toLowerCase().includes(q));
    render(filtered);
  });

  // Modal controls
  modal?.addEventListener('click', (e) => {
    if (e.target === modal || e.target.closest('.modal-close')) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal?.classList.contains('open')) closeModal();
  });

  initialized = true;
}

async function fetchImages() {
  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    return data.images || [];
  } catch {
    showToast('Error loading images', 'error');
    return [];
  }
}

function render(images) {
  if (!grid || !empty) return;
  grid.innerHTML = '';

  if (!images.length) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  const frag = document.createDocumentFragment();
  images.forEach(name => {
    const url = `${API}/${encodeURIComponent(name)}`;
    const div = document.createElement('div');
    div.className = 'gallery-item';
    div.innerHTML = `
      <div class="thumb">
        <button class="icon-btn btn-copy" title="Copy URL" data-name="${name}">
          <i class="fas fa-link"></i>
        </button>
        <button class="icon-btn btn-delete" title="Delete" data-name="${name}">
          <i class="fas fa-trash"></i>
        </button>
        <img src="${url}" alt="${name}" data-name="${name}">
      </div>
      <div class="caption">${name}</div>
    `;
    frag.appendChild(div);
  });
  grid.appendChild(frag);
}

function openModal(src, name) {
  if (!modal) return;
  modalImg.src = src;
  modalImg.alt = name;
  if (modalCaption) modalCaption.textContent = name;
  if (modalOpenLink) modalOpenLink.href = src;
  modal.classList.add('open');
}

function closeModal() {
  if (!modal) return;
  modal.classList.remove('open');
  modalImg.src = '';
  modalImg.alt = '';
}

export async function refreshMediaPage() {
  initOnce();
  if (!panel) return;
  const images = await fetchImages();
  lastImages = images;
  const q = (filterInput?.value || '').toLowerCase();
  render(q ? images.filter(n => n.toLowerCase().includes(q)) : images);
}
