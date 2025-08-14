// main.js
import { openPageModal } from './pageModal.js';
import { filterPages } from './pageService.js';
import { loadConfig, handleSubmit } from './config.js';
import { loadMailConfig, handleMailSubmit } from './mail.js';
import { refreshMediaPage } from './media.js';

document.addEventListener('DOMContentLoaded', () => {
  const $  = sel => document.querySelector(sel);
  const $$ = sel => [...document.querySelectorAll(sel)];

  const panels = $$('.main-content');
  const links  = $$('.sidebar-nav a');

  function showPanel(panelId) {
    panels.forEach(p => p.classList.toggle('active-panel', p.id === panelId));
    const linkId = panelId.replace('-panel', '-link');
    links.forEach(l => l.classList.toggle('active', l.id === linkId));
    if (panelId === 'media-panel') refreshMediaPage();
  }

  // Sidebar nav
  $('#pages-link') ?.addEventListener('click', e => { e.preventDefault(); showPanel('pages-panel'); });
  $('#config-link')?.addEventListener('click', e => { e.preventDefault(); showPanel('config-panel'); });
  $('#mail-link')  ?.addEventListener('click', e => { e.preventDefault(); showPanel('mail-panel'); });
  $('#media-link') ?.addEventListener('click', e => { e.preventDefault(); showPanel('media-panel'); });

  // Pages panel
  $('#add-page-btn')  ?.addEventListener('click', openPageModal);
  $('#empty-add-btn') ?.addEventListener('click', openPageModal);
  $('#search-input')  ?.addEventListener('input', filterPages);

  // Config/Mail forms
  $('#config-form')?.addEventListener('submit', handleSubmit);
  $('#mail-form')  ?.addEventListener('submit', handleMailSubmit);

  // Content type toggle
  $('#content-type')?.addEventListener('change', e => {
    const isMd = e.target.value === 'markdown';
    const md = $('#markdown-group');
    const html = $('#html-group');
    if (md)   md.style.display   = isMd ? 'block' : 'none';
    if (html) html.style.display = isMd ? 'none'  : 'block';
  });

  // Slug → external editor links
  const updateEditLinks = () => {
    const slug = ($('#page-slug')?.value || '').trim();
    const asta = $('#edit-with-asta');
    const aina = $('#edit-with-aina');
    if (asta) asta.href = `/asta?slug=${slug}`;
    if (aina) aina.href = `/aina?slug=${slug}`;
  };
  $('#page-slug')?.addEventListener('input', updateEditLinks);

  // Modal tabs (scoped to the page modal only)
  function initModalTabs() {
    const modal = $('#page-modal');
    if (!modal) return;

    modal.addEventListener('click', (e) => {
      const tab = e.target.closest('.tab');
      if (!tab || !modal.contains(tab)) return;

      const name = tab.dataset.tab; // 'content' | 'seo' | 'preview'

      // Toggle active state on tab headers
      modal.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t === tab));

      // Toggle active state on tab content panes
      modal.querySelectorAll('.tab-content').forEach(c =>
        c.classList.toggle('active', c.dataset.tabContent === name)
      );
    });
  }

  // Initialize data and UI
  loadConfig();
  loadMailConfig();
  updateEditLinks();
  initModalTabs();

  // Default panel
  showPanel('pages-panel');
});
