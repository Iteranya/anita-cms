// contextManager.js
import { showNotification } from './notifications.js';

// 📦 STATE MANAGEMENT
let activeContext = [];
let isInitialized = false; // Prevent double loading

/**
 * Initializes the Context Manager (Routes + Media + Prompt Inspector)
 */
export async function initContextManager() {
    
    // 1. Prevent double initialization
    if (isInitialized) {
        console.log("Context Manager already initialized, skipping.");
        return;
    }
    isInitialized = true;

    console.log("🔌 Initializing Context Manager...");

    // --- Select DOM Elements ---
    const routeSelect = document.getElementById('route-multi-select');
    const userTextArea = document.getElementById('content');
    
    // Media Panel Elements
    const mediaBtn = document.getElementById('btn-open-media-picker');
    const mediaDrawer = document.getElementById('media-picker-drawer');
    const closeMediaBtn = document.getElementById('btn-close-media');
    
    // Prompt Inspector Elements
    const promptDrawer = document.getElementById('prompt-inspector-drawer');
    const toggleDebugBtn = document.getElementById('btn-toggle-debug'); 
    const closeDebugBtn = document.getElementById('btn-close-debug');   
    const copyPromptBtn = document.getElementById('btn-copy-prompt');

    // -----------------------------------------------------------
    // ⚡ STEP 1: ATTACH LISTENERS IMMEDIATELY (UI First)
    // -----------------------------------------------------------

    // --- Media Drawer Event Listeners ---
    if (mediaBtn) {
        mediaBtn.addEventListener('click', (e) => {
            e.preventDefault(); // Stop any form submission
            console.log("Media button clicked");
            mediaDrawer.classList.toggle('hidden');
            
            // Only fetch images when opening
            if (!mediaDrawer.classList.contains('hidden')) {
                loadMediaAssets();
            }
        });
    } else {
        console.warn("⚠️ Media Button (btn-open-media-picker) not found in DOM");
    }

    if (closeMediaBtn) {
        closeMediaBtn.addEventListener('click', (e) => {
            e.preventDefault();
            mediaDrawer.classList.add('hidden');
        });
    }

    // --- Prompt Inspector Event Listeners ---
    if (toggleDebugBtn) {
        toggleDebugBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log("Debug toggle clicked");
            promptDrawer.classList.toggle('hidden');
        });
    } else {
        console.warn("⚠️ Debug Toggle (btn-toggle-debug) not found in DOM");
    }

    if (closeDebugBtn) {
        closeDebugBtn.addEventListener('click', (e) => {
            e.preventDefault();
            promptDrawer.classList.add('hidden');
        });
    }

    if (copyPromptBtn) {
        copyPromptBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const fullText = getEngineeredContext() + "\n\n### USER REQUEST ###\n" + (userTextArea ? userTextArea.value : "");
            navigator.clipboard.writeText(fullText).then(() => {
                showNotification('Prompt copied!', 'info');
            }).catch(err => {
                console.error('Failed to copy: ', err);
                showNotification('Failed to copy text.', 'error');
            });
        });
    }

    // Live Typing Update
    if (userTextArea) {
        userTextArea.addEventListener('input', () => {
            updateLivePromptPreview();
        });
    }

    // Route Selection Logic
    if (routeSelect) {
        routeSelect.addEventListener('change', async (e) => {
            const routeName = e.target.value;
            if (!routeName) return;
            
            if (activeContext.find(c => c.id === routeName && c.type === 'route')) {
                showNotification('That route is already added!', 'info');
                e.target.value = "";
                return;
            }

            await addRouteToContext(routeName);
            e.target.value = ""; 
        });
    }

    // Initial UI Render
    updateLivePromptPreview();

    // -----------------------------------------------------------
    // ⏳ STEP 2: LOAD ASYNC DATA (Network Last)
    // -----------------------------------------------------------
    console.log("⏳ Fetching API routes...");
    await loadRoutesIntoSelect(routeSelect);
}

/**
 * 🔌 API ROUTE LOGIC
 */
async function loadRoutesIntoSelect(selectElement) {
    if (!selectElement) return;

    try {
        const res = await fetch("/aina/routes");
        if (!res.ok) throw new Error("Failed to fetch routes");
        let routes = await res.json();

        // Inject 'media-data' definition if missing
        const mediaRouteExists = routes.find(r => r.name === 'media-data');
        if (!mediaRouteExists) {
            routes.push(getMediaDataRouteDefinition());
        }

        const groups = {};
        routes.forEach(r => {
            if (!groups[r.type]) groups[r.type] = [];
            groups[r.type].push(r);
        });

        for (const [type, items] of Object.entries(groups)) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = type.toUpperCase();
            items.forEach(item => {
                const opt = document.createElement('option');
                opt.value = item.name;
                opt.textContent = item.name;
                opt.dataset.schema = JSON.stringify(item);
                optgroup.appendChild(opt);
            });
            selectElement.appendChild(optgroup);
        }
    } catch (err) {
        console.error("Error loading routes (Non-fatal):", err);
        // We do NOT re-throw here, so the rest of the app keeps working
    }
}

async function addRouteToContext(routeName) {
    const select = document.getElementById('route-multi-select');
    let schemaData = null;
    
    for (const opt of select.querySelectorAll('option')) {
        if (opt.value === routeName) {
            schemaData = JSON.parse(opt.dataset.schema || "{}");
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
 * 🖼️ MEDIA LIBRARY LOGIC
 */
async function loadMediaAssets() {
    const grid = document.getElementById('media-grid');
    if (!grid) return;

    grid.innerHTML = '<div class="loading-spinner">Fetching media from system...</div>';

    try {
        const res = await fetch('/forms/media-data/submissions');
        
        if (!res.ok) {
            if(res.status === 404) throw new Error("Media form not initialized yet.");
            throw new Error("Failed to load media");
        }
        
        const submissions = await res.json();
        grid.innerHTML = ''; 

        if (submissions.length === 0) {
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; color:#777; padding: 20px;">No images found in media-data.</div>';
            return;
        }

        for (const sub of submissions) {
            const data = sub.data;
            const imgUrl = data.public_link;
            
            if (!imgUrl) continue;

            const item = document.createElement('div');
            item.className = 'media-item';
            
            if (activeContext.find(c => c.id === sub.id)) {
                item.classList.add('selected');
            }

            item.innerHTML = `
                <img src="${imgUrl}" loading="lazy" alt="${data.friendly_name || 'Image'}">
                <div class="title">${data.friendly_name || 'Untitled'}</div>
            `;

            item.addEventListener('click', () => toggleMediaSelection(item, sub));
            grid.appendChild(item);
        }
    } catch (err) {
        grid.innerHTML = `<div style="color:red; padding:10px; font-size: 0.9rem;">Error: ${err.message}</div>`;
    }
}

async function toggleMediaSelection(element, submission) {
    const id = submission.id;
    const data = submission.data;
    const index = activeContext.findIndex(c => c.id === id);

    if (index > -1) {
        activeContext.splice(index, 1);
        element.classList.remove('selected');
    } else {
        element.classList.add('selected');
        const ratio = await getImageRatio(data.public_link);
        activeContext.push({
            type: 'image',
            id: id,
            data: { ...data, aspectRatio: ratio },
            display: `IMG: ${data.friendly_name || 'Untitled'}`
        });
    }
    renderContextChips();
}

function getImageRatio(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(`${img.naturalWidth}x${img.naturalHeight}`);
        img.onerror = () => resolve("unknown");
        img.src = url;
    });
}

/**
 * 🧠 UI RENDERING & PROMPT GENERATION
 */
function renderContextChips() {
    const container = document.getElementById('active-context-container');
    if (!container) return;
    
    container.innerHTML = '';

    if (activeContext.length === 0) {
        container.innerHTML = '<span class="placeholder-text"><i class="fas fa-info-circle"></i> No context selected. AI will fly blind~</span>';
    } else {
        activeContext.forEach((item, index) => {
            const chip = document.createElement('div');
            chip.className = `context-chip type-${item.type}`;
            chip.innerHTML = `<span>${item.display}</span><i class="fas fa-times remove"></i>`;
            
            chip.querySelector('.remove').addEventListener('click', () => {
                activeContext.splice(index, 1);
                renderContextChips();
                if (item.type === 'image') {
                    const drawer = document.getElementById('media-picker-drawer');
                    if(drawer && !drawer.classList.contains('hidden')) loadMediaAssets();
                }
            });
            container.appendChild(chip);
        });
    }
    updateLivePromptPreview();
}

function updateLivePromptPreview() {
    const contextView = document.getElementById('debug-context-view');
    const userView = document.getElementById('debug-user-view');
    const userTextArea = document.getElementById('content');

    if (contextView) contextView.textContent = getEngineeredContext() || "(No system context selected)";
    if (userView && userTextArea) userView.textContent = userTextArea.value || "(Waiting for user input...)";
}

export function getEngineeredContext() {
    if (activeContext.length === 0) return "";

    let promptString = "\n\n### SYSTEM CONTEXT & RESOURCES ###\n";
    
    const routes = activeContext.filter(c => c.type === 'route');
    if (routes.length > 0) {
        promptString += "You have access to the following API Routes. USE THEM for functionality:\n";
        routes.forEach(r => {
            promptString += `
--- ROUTE: ${r.data.name} (${r.data.type}) ---
Description: ${r.data.usage_note || r.data.description || 'No specific notes'}
Schema: ${JSON.stringify(r.data.schema || {}, null, 0)}
`;
        });
    }

    const images = activeContext.filter(c => c.type === 'image');
    if (images.length > 0) {
        promptString += "\n### VISUAL ASSETS (Use these images in the HTML) ###\n";
        images.forEach(img => {
            promptString += `
--- IMAGE ASSET ---
Name: ${img.data.friendly_name}
URL: ${img.data.public_link}
Dimensions: ${img.data.aspectRatio}
USAGE: <img src="${img.data.public_link}" alt="${img.data.friendly_name}">
\n`;
        });
    }

    promptString += "### END CONTEXT ###\n\n";
    return promptString;
}

function getMediaDataRouteDefinition() {
    return {
        name: "media-data",
        type: "form",
        description: "System form for storing image metadata.",
        schema: {
            fields: [
                { name: "friendly_name", type: "text" },
                { name: "description", type: "textarea" },
                { name: "public_link", type: "text" }
            ]
        }
    };
}