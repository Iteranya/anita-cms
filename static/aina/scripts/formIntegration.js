// formIntegration.js

/**
 * Initializes the "Form Integration" sidebar:
 * - Toggles sidebar open/close
 * - Fetches available forms
 * - Loads schema of selected form into notes area
 */
export async function initFormGeneration(
    sidebar = document.getElementById('notes-sidebar'),
    toggleBtn = document.getElementById('sidebar-toggle'),
    formSelect = document.getElementById('form-select'),
    loadBtn = document.getElementById('load-form-btn'),
    notesArea = document.getElementById('notes-textarea')
) {
    // ----------------------------------------------------
    // 🕵️‍♀️ Element checks
    // ----------------------------------------------------
    if (!sidebar || !toggleBtn || !formSelect || !loadBtn || !notesArea) {
        console.warn("[FormIntegration] Missing one or more sidebar elements. Retrying after DOM ready...");
        document.addEventListener("DOMContentLoaded", () => {
            initFormGeneration(); // Retry after DOM is fully loaded
        });
        return;
    }
    toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    document.body.classList.toggle('sidebar-open');
});

    console.log("🧩 Form Integration initialized.");

    // ----------------------------------------------------
    // 🎚️ Sidebar toggle logic
    // ----------------------------------------------------
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        document.body.classList.toggle('sidebar-open');
    });

    // Optional hover behavior for cute arrow reveal
    toggleBtn.addEventListener('mouseenter', () => {
        toggleBtn.classList.add('visible');
    });
    toggleBtn.addEventListener('mouseleave', () => {
        if (!sidebar.classList.contains('open')) {
            toggleBtn.classList.remove('visible');
        }
    });

    // ----------------------------------------------------
    // 📜 Load available forms into the dropdown
    // ----------------------------------------------------
    async function loadForms() {
        try {
            const res = await fetch("/forms/list");
            if (!res.ok) throw new Error(`Failed to fetch forms: ${res.statusText}`);
            const forms = await res.json();

            // Clear dropdown
            formSelect.innerHTML = '<option value="">-- Select a form --</option>';

            // Populate dropdown with forms
            forms.forEach(f => {
                const opt = document.createElement("option");
                opt.value = f.slug;
                opt.textContent = f.title || f.slug;
                formSelect.appendChild(opt);
            });

            console.log(`📋 Loaded ${forms.length} forms into selector.`);
        } catch (err) {
            console.error("[FormIntegration] Error loading forms:", err);
        }
    }

    // ----------------------------------------------------
    // 📦 Load selected form's schema into notes textarea
    // ----------------------------------------------------
    loadBtn.addEventListener('click', async () => {
        const slug = formSelect.value;
        if (!slug) {
            alert("Please select a form first, senpai~");
            return;
        }

        try {
            const res = await fetch(`/forms/${slug}`);
            if (!res.ok) throw new Error(`Failed to load form data for ${slug}`);
            const form = await res.json();

            const formInfo = `
                # Form Info\nForm Name: ${form.title}\nForm Slug: ${form.slug}\nSubmission Endpoint: /forms/${form.slug}/submit\n# Submission Guide for AI\nWhen submitting this form, always POST a JSON body in this format:\n
                {
                "form_slug": "${form.slug}",
                "data": {
                    /* field_name: user_input */
                }
                }

                For example:
                {
                "form_slug": "${form.slug}",
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "message": "Hello from Aina!"
                }
                }

                # Schema
                ${JSON.stringify(form.schema, null, 2)}
                # Important Note: Use label for the data key value.
                # Important Note: Yes this is REAL application. Not Simulation, Not Demonstration, MAKE REAL IMPLEMENTATION
                `.trim();
            notesArea.value += formInfo;
            console.log(`✅ Loaded form schema for "${form.slug}" into notes.`);
        } catch (err) {
            console.error("[FormIntegration] Error loading form:", err);
        }
    });

    // ----------------------------------------------------
    // 🚀 Initialize dropdown on load
    // ----------------------------------------------------
    await loadForms();
}
