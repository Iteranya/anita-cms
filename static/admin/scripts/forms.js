import { showToast } from './toastService.js';

const formsList = document.getElementById('forms-list');
const newFormBtn = document.getElementById('new-form-btn');
const formEditorCard = document.getElementById('form-editor-card');
const formEditorTitle = document.getElementById('form-editor-title');
const formEditor = document.getElementById('form-editor');

const formSlug = document.getElementById('form-slug');
const formTitle = document.getElementById('form-title');
const formDescription = document.getElementById('form-description');
const formSchema = document.getElementById('form-schema');

const cancelEditBtn = document.getElementById('cancel-edit-btn');

let editingSlug = null;

// ----------------------------------------------------
// 🧭 Load and display forms
// ----------------------------------------------------
export async function loadForms() {
    try {
        const response = await fetch('/forms/list/');
        if (!response.ok) throw new Error('Failed to load forms');
        const forms = await response.json();
        console.log(forms)

        formsList.innerHTML = '';
        if (forms.length === 0) {
            formsList.innerHTML = `<tr><td colspan="5" style="text-align:center;">No forms yet.</td></tr>`;
            return;
        }

        forms.forEach(form => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${form.slug}</td>
                <td>${form.title}</td>
                <td>${form.description || '-'}</td>
                <td>${form.author || '-'}</td>
                <td>${form.updated || '-'}</td>
                <td>
                    <a href="/forms?slug=${form.slug}" class="btn btn-sm btn-primary view-btn">View</a>
                    <button class="btn btn-sm btn-secondary edit-btn" data-slug="${form.slug}">Edit</button>
                    <button class="btn btn-sm btn-danger delete-btn" data-slug="${form.slug}">Delete</button>
                </td>
            `;
            formsList.appendChild(row);
        });

        // Attach edit/delete events
        document.querySelectorAll('.edit-btn').forEach(btn => btn.addEventListener('click', () => editForm(btn.dataset.slug)));
        document.querySelectorAll('.delete-btn').forEach(btn => btn.addEventListener('click', () => deleteForm(btn.dataset.slug)));

    } catch (err) {
        console.error(err);
        showToast('Error loading forms', 'error');
    }
}

// ----------------------------------------------------
// ✏️ Create / Edit Form
// ----------------------------------------------------
newFormBtn.addEventListener('click', () => {
    editingSlug = null;
    formEditorTitle.textContent = 'Create Form';
    formEditor.reset();
    formEditorCard.style.display = 'block';
});

cancelEditBtn.addEventListener('click', () => {
    formEditorCard.style.display = 'none';
    formEditor.reset();
});

async function editForm(slug) {
    try {
        const response = await fetch(`/forms/${slug}`);
        if (!response.ok) throw new Error('Failed to load form');
        const form = await response.json();

        editingSlug = slug;
        formEditorTitle.textContent = `Edit Form: ${slug}`;
        formSlug.value = form.slug;
        formTitle.value = form.title;
        formDescription.value = form.description || '';
        populateFieldsFromSchema(form.schema);

        formEditorCard.style.display = 'block';
    } catch (err) {
        console.error(err);
        showToast('Error loading form for edit', 'error');
    }
}

// ----------------------------------------------------
// 💾 Save Form
// ----------------------------------------------------
formEditor.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
        slug: formSlug.value.trim(),
        title: formTitle.value.trim(),
        description: formDescription.value.trim(),
        schema: {}
    };

    try {
        payload.schema = collectSchema();
    } catch (err) {
        showToast('Invalid JSON in schema', 'error');
        return;
    }

    if (!payload.slug || !payload.title) {
        showToast('Slug and Title are required', 'error');
        return;
    }

    try {
        const method = editingSlug ? 'PUT' : 'POST';
        const url = editingSlug ? `/forms/${editingSlug}` : '/forms/';

        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Failed to ${editingSlug ? 'update' : 'create'} form`);
        showToast(`Form ${editingSlug ? 'updated' : 'created'} successfully`, 'success');

        formEditorCard.style.display = 'none';
        await loadForms();
        formEditor.reset();
        fieldsContainer.innerHTML = '';

    } catch (err) {
        console.error(err);
        showToast('Error saving form', 'error');
    }
});

// ----------------------------------------------------
// 🗑️ Delete Form
// ----------------------------------------------------
async function deleteForm(slug) {
    if (!confirm(`Delete form "${slug}"? This cannot be undone.`)) return;

    try {
        const response = await fetch(`/forms/${slug}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete form');
        showToast('Form deleted', 'success');
        await loadForms();
    } catch (err) {
        console.error(err);
        showToast('Error deleting form', 'error');
    }
}

const fieldsContainer = document.getElementById('fields-container');
const addFieldBtn = document.getElementById('add-field-btn');

// 🧱 Template for new field rows
function createFieldRow(field = { name: '', label: '', type: 'text', required: false }) {
    const row = document.createElement('div');
    row.classList.add('field-row', 'd-flex', 'gap-2', 'align-items-center', 'mb-2');

    row.innerHTML = `
        <input type="text" class="form-control field-name" placeholder="Field name" value="${field.name}">
        <input type="text" class="form-control field-label" placeholder="Label" value="${field.label}">
        <select class="form-control field-type">
            <option value="text" ${field.type === 'text' ? 'selected' : ''}>Text</option>
            <option value="email" ${field.type === 'email' ? 'selected' : ''}>Email</option>
            <option value="number" ${field.type === 'number' ? 'selected' : ''}>Number</option>
            <option value="textarea" ${field.type === 'textarea' ? 'selected' : ''}>Textarea</option>
            <option value="checkbox" ${field.type === 'checkbox' ? 'selected' : ''}>Checkbox</option>
        </select>
        <label class="d-flex align-items-center gap-1">
            <input type="checkbox" class="field-required" ${field.required ? 'checked' : ''}> Required
        </label>
        <button type="button" class="btn btn-sm btn-danger remove-field-btn">✖</button>
    `;

    row.querySelector('.remove-field-btn').addEventListener('click', () => row.remove());
    return row;
}

addFieldBtn.addEventListener('click', () => {
    fieldsContainer.appendChild(createFieldRow());
});

// 🔄 Populate fields when editing
function populateFieldsFromSchema(schema) {
    fieldsContainer.innerHTML = '';
    if (schema && Array.isArray(schema.fields)) {
        schema.fields.forEach(f => fieldsContainer.appendChild(createFieldRow(f)));
    }
}

// 🧬 Generate schema before saving
function collectSchema() {
    const fields = [];
    fieldsContainer.querySelectorAll('.field-row').forEach(row => {
        fields.push({
            name: row.querySelector('.field-name').value.trim(),
            label: row.querySelector('.field-label').value.trim(),
            type: row.querySelector('.field-type').value,
            required: row.querySelector('.field-required').checked
        });
    });
    return { fields };
}

// ----------------------------------------------------
// 🚀 Init
// ----------------------------------------------------
document.addEventListener('DOMContentLoaded', loadForms);
