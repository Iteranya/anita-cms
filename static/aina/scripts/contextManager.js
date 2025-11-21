// contextManager.js
import { showNotification } from './notifications.js';

// 📦 STATE MANAGEMENT
// Stores selected context items { type: 'route'|'image', id: string, data: object }
let activeContext = [];

/**
 * Initializes the Context Manager (Routes + Media)
 */
export async function initContextManager() {
    const routeSelect = document.getElementById('route-multi-select');
    const mediaBtn = document.getElementById('btn-open-media-picker');
    const mediaDrawer = document.getElementById('media-picker-drawer');
    const closeMediaBtn = document.getElementById('btn-close-media');

    // 1. Initialize Routes
    await loadRoutesIntoSelect(routeSelect);

    // 2. Initialize Media
    mediaBtn.addEventListener('click', () => {
        mediaDrawer.classList.remove('hidden');
        loadMediaAssets(); // Fetch fresh when opening
    });

    closeMediaBtn.addEventListener('click', () => {
        mediaDrawer.classList.add('hidden');
    });

    // 3. Event Listener for Route Selection
    routeSelect.addEventListener('change', async (e) => {
        const routeName = e.target.value;
        if (!routeName) return;
        
        // Don't add duplicates
        if (activeContext.find(c => c.id === routeName && c.type === 'route')) {
            showNotification('That route is already added!', 'info');
            e.target.value = "";
            return;
        }

        await addRouteToContext(routeName);
        e.target.value = ""; // Reset dropdown
    });
}

/**
 * Loads routes from API into the dropdown
 */
async function loadRoutesIntoSelect(selectElement) {
    try {
        const res = await fetch("/aina/routes");
        if (!res.ok) throw new Error("Failed to fetch routes");
        let routes = await res.json();

        // ✨ "Slip in" the media-data route manually if not present
        const mediaRouteExists = routes.find(r => r.name === 'media-data');
        if (!mediaRouteExists) {
            routes.push(getMediaDataRouteDefinition());
        }

        // Group by Type
        const groups = {};
        routes.forEach(r => {
            if (!groups[r.type]) groups[r.type] = [];
            groups[r.type].push(r);
        });

        // Build Options
        for (const [type, items] of Object.entries(groups)) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = type.toUpperCase();
            items.forEach(item => {
                const opt = document.createElement('option');
                opt.value = item.name;
                opt.textContent = item.name;
                opt.dataset.schema = JSON.stringify(item); // Store schema in DOM
                optgroup.appendChild(opt);
            });
            selectElement.appendChild(optgroup);
        }
    } catch (err) {
        console.error("Error loading routes:", err);
    }
}

/**
 * Adds a specific route to the active context array
 */
async function addRouteToContext(routeName) {
    // Find schema (we could fetch again, or grab from cached/DOM)
    // For robustness, let's fetch specific info or find in current list
    // Simulating find in DOM for speed:
    const select = document.getElementById('route-multi-select');
    let schemaData = null;
    
    // Find option across optgroups
    for (const opt of select.querySelectorAll('option')) {
        if (opt.value === routeName) {
            schemaData = JSON.parse(opt.dataset.schema);
            break;
        }
    }

    if (schemaData) {
        activeContext.push({
            type: 'route',
            id: routeName,
            data: schemaData,
            display: `API: ${routeName}`
        });
        renderContextChips();
    }
}

/**
 * 🖼️ MEDIA LOGIC
 * Fetches submissions from the "media-data" form
 */
async function loadMediaAssets() {
    const grid = document.getElementById('media-grid');
    grid.innerHTML = '<div class="loading-spinner">Fetching media from system...</div>';

    try {
        // Use the route specified in the prompt
        const res = await fetch('/forms/media-data/submissions');
        
        if (!res.ok) {
            if(res.status === 404) throw new Error("Media form not initialized yet.");
            throw new Error("Failed to load media");
        }
        
        const submissions = await res.json();
        grid.innerHTML = ''; // Clear loading

        if (submissions.length === 0) {
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; color:#777;">No images found in media-data.</div>';
            return;
        }

        for (const sub of submissions) {
            const data = sub.data; // The field data
            const imgUrl = data.public_link;
            
            const item = document.createElement('div');
            item.className = 'media-item';
            // Check if already selected
            if (activeContext.find(c => c.id === sub.id)) item.classList.add('selected');

            item.innerHTML = `
                <img src="${imgUrl}" loading="lazy" alt="${data.friendly_name}">
                <div class="title">${data.friendly_name}</div>
            `;

            // Click to toggle
            item.addEventListener('click', () => toggleMediaSelection(item, sub));
            grid.appendChild(item);
        }
    } catch (err) {
        grid.innerHTML = `<div style="color:red; padding:10px;">Error: ${err.message}</div>`;
    }
}

/**
 * Toggles image selection and calculates aspect ratio
 */
async function toggleMediaSelection(element, submission) {
    const id = submission.id;
    const data = submission.data;
    
    // Check if exists
    const index = activeContext.findIndex(c => c.id === id);

    if (index > -1) {
        // Remove
        activeContext.splice(index, 1);
        element.classList.remove('selected');
    } else {
        // Add
        element.classList.add('selected'); // Visual feedback immediately
        
        // Calculate Ratio
        const ratio = await getImageRatio(data.public_link);
        
        activeContext.push({
            type: 'image',
            id: id,
            data: { ...data, aspectRatio: ratio }, // Merge ratio into data
            display: `IMG: ${data.friendly_name}`
        });
    }
    renderContextChips();
}

/**
 * Helper: Load image in background to get dimensions
 */
function getImageRatio(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const w = img.naturalWidth;
            const h = img.naturalHeight;
            // Simple GCD function for pretty ratio (optional), or just raw
            resolve(`${w}x${h}`);
        };
        img.onerror = () => resolve("unknown");
        img.src = url;
    });
}

/**
 * Renders the chips at the top
 */
function renderContextChips() {
    const container = document.getElementById('active-context-container');
    container.innerHTML = '';

    if (activeContext.length === 0) {
        container.innerHTML = '<span class="placeholder-text">No context selected. AI will fly blind~</span>';
        return;
    }

    activeContext.forEach((item, index) => {
        const chip = document.createElement('div');
        chip.className = `context-chip type-${item.type}`;
        chip.innerHTML = `
            <span>${item.display}</span>
            <i class="fas fa-times remove"></i>
        `;
        
        // Remove handler
        chip.querySelector('.remove').addEventListener('click', () => {
            activeContext.splice(index, 1);
            renderContextChips();
            
            // If media drawer is open, update selection state visually
            if (item.type === 'image') {
                loadMediaAssets(); // Brute force refresh of grid classes
            }
        });
        
        container.appendChild(chip);
    });
}

/**
 * 🧠 EXPORT: Gets the final engineered prompt string
 * call this from your aiIntegration.js before sending
 */
export function getEngineeredContext() {
    if (activeContext.length === 0) return "";

    let promptString = "\n\n### SYSTEM CONTEXT & RESOURCES ###\n";

    // 1. Process Routes
    const routes = activeContext.filter(c => c.type === 'route');
    if (routes.length > 0) {
        promptString += "You have access to the following API Routes. USE THEM for functionality:\n";
        routes.forEach(r => {
            promptString += `
--- ROUTE: ${r.data.name} (${r.data.type}) ---
Description: ${r.data.description}
Endpoint: /forms/${r.data.name}/submit (for POST)
Schema (Fields): ${JSON.stringify(r.data.schema.fields)}
\n`;
        });
    }

    // 2. Process Images
    const images = activeContext.filter(c => c.type === 'image');
    if (images.length > 0) {
        promptString += "\n### VISUAL ASSETS (Use these images in the HTML) ###\n";
        images.forEach(img => {
            promptString += `
--- IMAGE ASSET ---
Name: ${img.data.friendly_name}
URL: ${img.data.public_link}
Description: ${img.data.description || 'No description'}
Dimensions: ${img.data.aspectRatio}
USAGE: Use <img src="${img.data.public_link}" alt="${img.data.friendly_name}">
\n`;
        });
    }

    promptString += "### END CONTEXT ###\n\n";
    return promptString;
}

/**
 * Hardcoded fallback for the media-data route
 */
function getMediaDataRouteDefinition() {
    return {
        name: "media-data",
        type: "form",
        description: "System form for storing image metadata.",
        schema: {
            fields: [
                { name: "friendly_name", type: "text" },
                { name: "description", type: "textarea" },
                { name: "saved_filename", type: "text" },
                { name: "public_link", type: "text" }
            ]
        }
    };
}