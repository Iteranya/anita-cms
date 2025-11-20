// main.js - Entry point
import { initPreview, updatePreview } from './previewManager.js';
import { initAiGeneration } from './aiIntegration.js';
import { setupFileHandlers } from './fileHandler.js';
import { setupDeployment } from './deploymentService.js';
import { setupEffects } from './effects.js';
import { initFormGeneration } from './formIntegration.js'; // Legacy support
import { initRouteHelper } from './routeHelper.js'; // New Route Helper

// --------------------------------------------------
// 🚀 DOM LOADED HANDLER
// --------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
    // --- Grab key DOM elements safely ---
    const htmlCode = document.getElementById('html-code');
    const preview = document.getElementById('preview');
    const slugContainer = document.getElementById('slug-container');
    const slug = slugContainer ? slugContainer.textContent.trim() : "";
    const notesArea = document.getElementById('notes-textarea');

    // Sidebar / Legacy Form Elements (For backward compatibility)
    // Note: In the new UI, these might be hidden dummy elements
    const sidebar = document.getElementById('notes-sidebar'); 
    const toggleBtn = document.getElementById('sidebar-toggle');
    const formSelect = document.getElementById('form-select'); // This might be null in new UI
    const loadBtn = document.getElementById('load-form-btn');  // This might be null in new UI

    // --- Sanity check ---
    if (!htmlCode || !preview) {
        console.error("Critical elements missing: html-code or preview.");
        return;
    }

    // --- Load the welcome template into the editor ---
    if (!htmlCode.value.trim()) { // Only load if empty
        htmlCode.value = `
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Aina's Playground!</title>
    <style>
        body {
            font-family: 'Comic Sans MS', cursive, sans-serif;
            background: linear-gradient(135deg, #f5f9fa 0%, #e0f7fa 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .welcome-box {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            max-width: 500px;
        }
        h1 {
            color: #4CAF50;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
        .kawaii {
            font-size: 2rem;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="welcome-box">
        <h1>Konnichiwa! (◕‿◕✿)</h1>
        <div class="kawaii">(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧</div>
        <p>Start coding in the editor and see your creation come to life here!</p>
        <p>Or describe your dream website below and let me generate it for you~</p>
    </div>
</body>
</html>`.trim();
    }

    // --------------------------------------------------
    // ⚙️ Initialize Features
    // --------------------------------------------------
    try {
        // 1. Initialize UI (Tabs, Resizer, Maximize)
        // We run this first so the layout is interactive immediately

        // 2. Preview System
        await initPreview(htmlCode, preview, slug);

        // 4. File Handlers
        setupFileHandlers(htmlCode, updatePreview);

        // 5. Deployment
        setupDeployment(htmlCode, slug);

        // 6. Route Helper (The new API tool)
        // This looks for #route-type-select and #route-item-select
        initRouteHelper();

        // 8. Visual Effects
        setupEffects();

        setupDojoUI(); 

        console.log("✅ All systems initialized successfully!");
    } catch (err) {
        console.error("Initialization error:", err);
    }
});

// --------------------------------------------------
// 🎨 UI LOGIC (Tabs, Resizer, Maximize)
// --------------------------------------------------
function setupDojoUI() {
    console.log("🎨 Setting up Dojo UI...");

    // --- A. TAB LOGIC ---
    const tabs = document.querySelectorAll('.tab-btn');
    const panes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-tab');
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // --- B. RESIZER LOGIC ---
    const container = document.getElementById('panes-container');
    const leftPane = document.getElementById('editor-pane');
    const rightPane = document.getElementById('preview-pane');
    const gutter = document.getElementById('resizer-gutter');
    
    if (container && leftPane && rightPane && gutter) {
        let isDragging = false;

        // Start Drag
        gutter.addEventListener('mousedown', (e) => {
            isDragging = true;
            e.preventDefault(); // Stop text selection
            container.classList.add('is-dragging');
            gutter.classList.add('active');
        });

        // End Drag
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                container.classList.remove('is-dragging');
                gutter.classList.remove('active');
            }
        });

        // Move Drag
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const containerRect = container.getBoundingClientRect();
            // Calculate % position relative to container
            let newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;

            // Clamp between 10% and 90%
            if (newLeftWidth < 10) newLeftWidth = 10;
            if (newLeftWidth > 90) newLeftWidth = 90;

            leftPane.style.width = `${newLeftWidth}%`;
            rightPane.style.width = `${100 - newLeftWidth}%`;
        });

        // Double Click Gutter -> Reset
        gutter.addEventListener('dblclick', () => {
            leftPane.style.width = '50%';
            rightPane.style.width = '50%';
            resetIcons();
        });
    }

    // --- C. MAXIMIZE BUTTON LOGIC ---
    const btnEditor = document.getElementById('btn-max-editor');
    const btnPreview = document.getElementById('btn-max-preview');

    // Helper to reset all icons to "expand"
    const resetIcons = () => {
        if(btnEditor) btnEditor.querySelector('i').className = 'fas fa-expand';
        if(btnPreview) btnPreview.querySelector('i').className = 'fas fa-expand';
    };

    // Maximize Editor Click
    if (btnEditor) {
        btnEditor.addEventListener('click', () => {
            if (leftPane.style.width === '100%') {
                // Restore 50/50
                leftPane.style.width = '50%';
                rightPane.style.width = '50%';
                resetIcons();
            } else {
                // Maximize Editor
                leftPane.style.width = '100%';
                rightPane.style.width = '0%';
                resetIcons();
                btnEditor.querySelector('i').className = 'fas fa-compress';
            }
        });
    }

    // Maximize Preview Click
    if (btnPreview) {
        btnPreview.addEventListener('click', () => {
            if (rightPane.style.width === '100%') {
                // Restore 50/50
                leftPane.style.width = '50%';
                rightPane.style.width = '50%';
                resetIcons();
            } else {
                // Maximize Preview
                rightPane.style.width = '100%';
                leftPane.style.width = '0%';
                resetIcons();
                btnPreview.querySelector('i').className = 'fas fa-compress';
            }
        });
    }
}