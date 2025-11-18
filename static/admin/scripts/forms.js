import { showToast } from './toastService.js';

const formsList = document.getElementById('forms-list');
const newFormBtn = document.getElementById('new-form-btn');
const formEditorCard = document.getElementById('form-editor-card');
const formEditorTitle = document.getElementById('form-editor-title');
const formEditor = document.getElementById('form-editor');
const tagsFilterContainer = document.getElementById('tags-filter-container'); // 🏷️ NEW

const formSlug = document.getElementById('form-slug');
const formTitle = document.getElementById('form-title');
const formDescription = document.getElementById('form-description');
const formTags = document.getElementById('form-tags'); // 🏷️ NEW
const formSchema = document.getElementById('form-schema');

const cancelEditBtn = document.getElementById('cancel-edit-btn');

let editingSlug = null;

// ----------------------------------------------------
// 🏷️ Load and display tags for filtering
// ----------------------------------------------------
async function loadAndDisplayTags() {
    try {
        const response = await fetch('/forms/tags/all');
        if (!response.ok) throw new Error('Failed to load tags');
        const tags = await response.json();

        tagsFilterContainer.innerHTML = '<strong>Filter by tag:</strong> ';
        
        const allBtn = document.createElement('button');
        allBtn.className = 'btn btn-sm btn-outline-secondary me-1';
        allBtn.textContent = 'All';
        allBtn.addEventListener('click', () => loadForms());
        tagsFilterContainer.appendChild(allBtn);

        tags.forEach(tag => {
            const tagBtn = document.createElement('button');
            tagBtn.className = 'btn btn-sm btn-outline-info me-1';
            tagBtn.textContent = tag;
            tagBtn.addEventListener('click', () => loadForms(tag));
            tagsFilterContainer.appendChild(tagBtn);
        });

    } catch(err) {
        console.error(err);
        tagsFilterContainer.innerHTML = '<small>Could not load tags.</small>';
    }
}
// ----------------------------------------------------
// 🧭 Load and display forms
// ----------------------------------------------------
// ----------------------------------------------------
// 🧭 Load and display forms
// ----------------------------------------------------
// ----------------------------------------------------
// 🧭 Load and display forms
// ----------------------------------------------------
export async function loadForms(tag = '') {
    try {
        const url = tag ? `/forms/list/?tag=${encodeURIComponent(tag)}` : '/forms/list/';
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load forms');
        const forms = await response.json();

        formsList.innerHTML = '';
        if (forms.length === 0) {
            formsList.innerHTML = `<tr><td colspan="6" style="text-align:center;">No forms found.</td></tr>`;
            return;
        }

        forms.forEach(form => {
            const row = document.createElement('tr');

            // --- Create Cells (No changes here) ---
            const titleCell = document.createElement('td');
            titleCell.textContent = form.title;
            const descCell = document.createElement('td');
            descCell.textContent = form.description || '-';
            const tagsCell = document.createElement('td');
            tagsCell.innerHTML = (form.tags && form.tags.length > 0)
                ? form.tags.map(t => `<span class="badge bg-secondary me-1">${t}</span>`).join('')
                : '-';
            const authorCell = document.createElement('td');
            authorCell.textContent = form.author || '-';
            const updatedCell = document.createElement('td');
            const updatedDate = form.updated ? new Date(form.updated) : null;
            updatedCell.textContent = updatedDate
                ? updatedDate.toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
                : '-';
            updatedCell.title = form.updated || '';
            const actionsCell = document.createElement('td');

            // --- Create Action Buttons ---

            // ✨ --- MODIFICATION START --- ✨
            // View Button (now a real <button> that navigates via JavaScript)
            const viewBtn = document.createElement('button'); // Changed from 'a'
            viewBtn.className = 'btn btn-sm form-view-btn';
            viewBtn.title = 'View Form';
            viewBtn.innerHTML = '<i class="fas fa-eye text-secondary"></i>';
            viewBtn.addEventListener('click', () => {
                window.location.href = `/forms?slug=${form.slug}`;
            });
            // ✨ --- MODIFICATION END --- ✨

            // Edit Button
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-sm form-edit-btn';
            editBtn.title = 'Edit Form';
            editBtn.innerHTML = '<i class="fas fa-pen-to-square text-secondary"></i>'; 
            editBtn.addEventListener('click', () => editForm(form.slug));

            // Delete Button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm form-delete-btn';
            deleteBtn.title = 'Delete Form';
            deleteBtn.innerHTML = '<i class="fas fa-trash text-danger"></i>'; 
            deleteBtn.addEventListener('click', () => deleteForm(form.slug));

            // --- Assemble Row ---
            actionsCell.append(viewBtn, editBtn, deleteBtn);
            row.append(titleCell, descCell, tagsCell, authorCell, updatedCell, actionsCell);
            formsList.appendChild(row);
        });

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
    fieldsContainer.innerHTML = ''; // Clear fields
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
        formTags.value = form.tags ? form.tags.join(', ') : ''; // 🏷️ NEW: Populate tags input
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

    // 🏷️ NEW: Process tags from the input field into an array
    const tagsArray = formTags.value.trim()
        ? formTags.value.split(',').map(tag => tag.trim()).filter(Boolean)
        : [];

    const payload = {
        slug: formSlug.value.trim(),
        title: formTitle.value.trim(),
        description: formDescription.value.trim(),
        tags: tagsArray, // 🏷️ NEW
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

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to ${editingSlug ? 'update' : 'create'} form`);
        }
        showToast(`Form ${editingSlug ? 'updated' : 'created'} successfully`, 'success');

        formEditorCard.style.display = 'none';
        await loadForms();
        await loadAndDisplayTags(); // 🏷️ NEW: Refresh tags in case new ones were added
        formEditor.reset();
        fieldsContainer.innerHTML = '';

    } catch (err) {
        console.error(err);
        showToast(err.message || 'Error saving form', 'error');
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
        await loadAndDisplayTags(); // 🏷️ NEW: Refresh tags in case some are now unused
    } catch (err) {
        console.error(err);
        showToast('Error deleting form', 'error');
    }
}


// ----------------------------------------------------
// SCHEMA FIELD BUILDER (No changes here)
// ----------------------------------------------------
const fieldsContainer = document.getElementById('fields-container');
const addFieldBtn = document.getElementById('add-field-btn');

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

function populateFieldsFromSchema(schema) {
    fieldsContainer.innerHTML = '';
    if (schema && Array.isArray(schema.fields)) {
        schema.fields.forEach(f => fieldsContainer.appendChild(createFieldRow(f)));
    }
}

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

// // ----------------------------------------------------
// // 🚀 Init
// // ----------------------------------------------------
// document.addEventListener('DOMContentLoaded', async () => { // ✨ ADD async HERE
//     await loadForms();           // ✨ ADD await HERE
//     await loadAndDisplayTags();  // ✨ ADD await HERE
// });