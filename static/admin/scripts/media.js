// media.js
import { showToast } from './toastService.js';

const API = '/media';

let grid, empty, fileIn, filterInput, uploadBtn, emptyUploadBtn, modal, modalImg, modalCaption, modalOpenLink;
let lastImages = [];
let initialized = false;

function $(id) { return document.getElementById(id); }

function initOnce() {
  if (initialized) return;

  grid           = $('gallery-grid');
  empty          = $('empty-state');
  fileIn         = $('file-picker');
  filterInput    = $('filter-input');
  uploadBtn      = $('upload-btn');
  emptyUploadBtn = $('empty-upload-btn');
  modal          = $('media-modal');
  modalImg       = $('media-modal-img');
  modalCaption   = $('media-modal-caption');
  modalOpenLink  = $('media-modal-open');

  if (!grid) return; // panel not in DOM

  // Grid actions: open, delete, copy
  grid.addEventListener('click', async (e) => {
    const del = e.target.closest('.btn-delete');
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
  uploadBtn?.addEventListener('click', openPicker);
  emptyUploadBtn?.addEventListener('click', openPicker);

  fileIn?.addEventListener('change', async () => {
    if (!fileIn.files[0]) return;
    const file = fileIn.files[0];
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await fetch(API, { method: 'POST', body: fd });
      if (!res.ok) throw new Error(await res.text());
      showToast('Upload successful', 'success');
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
        <img src="${url}" alt="${name}" data-name="${name}">
        <button class="icon-btn btn-copy" title="Copy URL" data-name="${name}">
          <i class="fas fa-copy"></i>
        </button>
        <button class="icon-btn btn-delete" title="Delete" data-name="${name}">
          <i class="fas fa-trash"></i>
        </button>
      </div>
      <div class="caption" title="${name}">${name}</div>
    `;
    frag.appendChild(div);
  });
  grid.appendChild(frag);
}

function openModal(src, name) {
  if (!modal) return;
  modalImg.src = src;
  modalImg.alt = name;
  modalCaption.textContent = name;
  modalOpenLink.href = src;
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
  const images = await fetchImages();
  lastImages = images;
  const q = (filterInput?.value || '').toLowerCase();
  render(q ? images.filter(n => n.toLowerCase().includes(q)) : images);
}
