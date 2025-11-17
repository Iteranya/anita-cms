// routeHelper.js

/**
 * Initializes the "API Route Helper" sidebar.
 * - Fetches all available routes from the backend.
 * - Populates a type-selector dropdown (e.g., 'form', 'page').
 * - Populates an item-selector dropdown based on the selected type.
 * - Loads formatted information about the selected route into the notes area.
 */
export async function initRouteHelper() {
    // ----------------------------------------------------
    // 🕵️‍♀️ Get all the kawaii elements from the DOM
    // ----------------------------------------------------
    const sidebar = document.getElementById('notes-sidebar');
    const typeSelect = document.getElementById('route-type-select');
    const itemSelect = document.getElementById('route-item-select');
    const loadBtn = document.getElementById('load-route-btn');
    const notesArea = document.getElementById('notes-textarea');
    const toggleBtn = document.getElementById('sidebar-toggle'); // Keep toggle logic

    if (!sidebar || !typeSelect || !itemSelect || !loadBtn || !notesArea || !toggleBtn) {
        console.error("[RouteHelper] ❌ Critical Error: Could not find one or more essential sidebar elements! Check your HTML IDs.");
        return;
        

    }
    console.log("✅ Found all sidebar elements.");
    // This can be removed from the main html file now
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        document.body.classList.toggle('sidebar-open');
    });

    let allRoutes = []; // Cache for all routes fetched from the API

    // ----------------------------------------------------
    // 📜 1. Fetch all routes and populate the TYPE dropdown
    // ----------------------------------------------------
    async function loadInitialData() {
        try {
            const res = await fetch("/aina/routes");
            if (!res.ok) throw new Error(`Failed to fetch routes: ${res.statusText}`);
            allRoutes = await res.json();

            // Get unique types (e.g., ['form', 'page', 'media'])
            const uniqueTypes = [...new Set(allRoutes.map(route => route.type))];

            // Clear and populate the type selector
            typeSelect.innerHTML = '<option value="">-- Select a type --</option>';
            uniqueTypes.forEach(type => {
                const opt = document.createElement("option");
                opt.value = type;
                // Capitalize first letter for display
                opt.textContent = type.charAt(0).toUpperCase() + type.slice(1);
                typeSelect.appendChild(opt);
            });

            console.log(`📋 Found ${uniqueTypes.length} route types.`);
        } catch (err) {
            console.error("[RouteHelper] Error loading initial data:", err);
            typeSelect.innerHTML = '<option value="">Error loading types</option>';
        }
    }

    // ----------------------------------------------------
    // 🔄 2. When a TYPE is selected, populate the ITEM dropdown
    // ----------------------------------------------------
    typeSelect.addEventListener('change', () => {
        const selectedType = typeSelect.value;
        itemSelect.innerHTML = '<option value="">-- Select an item --</option>'; // Reset

        if (!selectedType) {
            itemSelect.disabled = true;
            loadBtn.disabled = true;
            return;
        }

        const itemsOfType = allRoutes.filter(route => route.type === selectedType);

        itemsOfType.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.name; // Use the unique name/slug as the value
            opt.textContent = item.name;
            itemSelect.appendChild(opt);
        });

        itemSelect.disabled = false;
        loadBtn.disabled = true; // Keep load button disabled until an item is chosen
        console.log(`🗂️ Displaying ${itemsOfType.length} items of type "${selectedType}".`);
    });

    // ----------------------------------------------------
    // 🤔 3. Enable the Load button only when an item is selected
    // ----------------------------------------------------
    itemSelect.addEventListener('change', () => {
        loadBtn.disabled = !itemSelect.value;
    });

    // ----------------------------------------------------
    // 📦 4. When LOAD is clicked, format and display the info
    // ----------------------------------------------------
    loadBtn.addEventListener('click', () => {
        const selectedName = itemSelect.value;
        if (!selectedName) return;

        const selectedRoute = allRoutes.find(route => route.name === selectedName);
        if (!selectedRoute) {
            console.error(`Could not find route with name: ${selectedName}`);
            return;
        }

        const routeInfo = formatRouteInfo(selectedRoute);
        notesArea.value += `\n\n${routeInfo}`;
        notesArea.scrollTop = notesArea.scrollHeight; // Scroll to bottom

        console.log(`✅ Loaded info for "${selectedRoute.name}".`);
    });

    /**
     * Formats the RouteData object into a pretty, readable Markdown string.
     * @param {object} route The route data object.
     * @returns {string} A formatted string for the textarea.
     */
    function formatRouteInfo(route) {
        // A special note for forms, as requested in your original code
        const formSubmissionGuide = `
# Submission Guide for AI
When submitting this form, always POST a JSON body to the endpoint /forms/${route.name}/submit in this format:
\`\`\`json
{
  "form_slug": "${route.name}",
  "data": {
    /* field_name: user_input */
    /* Use the 'name' from the schema below, not the 'label' */
  }
}
\`\`\`
`;
        return `
# ---------------------------------
# Route: ${route.name}
# Type: ${route.type}
# ---------------------------------

## Description
${route.description || 'No description provided.'}

## Usage Note
${route.usage_note || 'No specific usage notes.'}
${route.type === 'form' ? formSubmissionGuide : ''}
## Schema / Metadata
\`\`\`json
${JSON.stringify(route.schema, null, 2)}
\`\`\`
        `.trim();
    }

    // ----------------------------------------------------
    // 🚀 Let's go!
    // ----------------------------------------------------
    await loadInitialData();
}