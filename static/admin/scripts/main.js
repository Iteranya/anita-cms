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
    // Toggle panels
    panels.forEach(p => p.classList.toggle('active-panel', p.id === panelId));
    // Toggle active link (map -panel -> -link)
    const linkId = panelId.replace('-panel', '-link');
    links.forEach(l => l.classList.toggle('active', l.id === linkId));

    // Lazy refresh media when entering media panel
    if (panelId === 'media-panel') refreshMediaPage();
  }

  // Nav links
  $('#pages-link') ?.addEventListener('click', e => { e.preventDefault(); showPanel('pages-panel'); });
  $('#config-link')?.addEventListener('click', e => { e.preventDefault(); showPanel('config-panel'); });
  $('#mail-link')  ?.addEventListener('click', e => { e.preventDefault(); showPanel('mail-panel'); });
  $('#media-link') ?.addEventListener('click', e => { e.preventDefault(); showPanel('media-panel'); });

  // Pages
  $('#add-page-btn')   ?.addEventListener('click', openPageModal);
  $('#empty-add-btn')  ?.addEventListener('click', openPageModal);
  $('#search-input')   ?.addEventListener('input', filterPages);

  // Config + Mail forms
  $('#config-form')?.addEventListener('submit', handleSubmit);
  $('#mail-form')  ?.addEventListener('submit', handleMailSubmit);

  // Content type toggle
  $('#content-type')?.addEventListener('change', e => {
    const isMd = e.target.value === 'markdown';
    $('#markdown-group') && ($('#markdown-group').style.display = isMd ? 'block' : 'none');
    $('#html-group')     && ($('#html-group').style.display     = isMd ? 'none'  : 'block');
  });

  // Slug → external editor links
  const updateEditLinks = () => {
    const slug = ($('#page-slug')?.value || '').trim();
    $('#edit-with-asta') && ($('#edit-with-asta').href = `/asta?slug=${slug}`);
    $('#edit-with-aina') && ($('#edit-with-aina').href = `/aina?slug=${slug}`);
  };
  $('#page-slug')?.addEventListener('input', updateEditLinks);

  // Initialize data
  loadConfig();
  loadMailConfig();
  updateEditLinks();

  // Default panel
  showPanel('pages-panel');
});
