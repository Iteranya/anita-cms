// main.js - Entry point
import { initPreview, updatePreview } from './previewManager.js';
import { initAiGeneration } from './aiIntegration.js';
import { setupFileHandlers } from './fileHandler.js';
import { setupDeployment } from './deploymentService.js';
import { setupEffects } from './effects.js';
import { initFormGeneration } from './formIntegration.js';

// --------------------------------------------------
// 🚀 DOM LOADED HANDLER
// --------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
    // --- Grab key DOM elements safely ---
    const htmlCode = document.getElementById('html-code');
    const preview = document.getElementById('preview');
    const slugContainer = document.getElementById('slug-container');
    const slug = slugContainer ? slugContainer.textContent.trim() : "";
    
    // Sidebar + form UI elements
    const sidebar = document.getElementById('notes-sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const formSelect = document.getElementById('form-select');
    const loadBtn = document.getElementById('load-form-btn');
    const notesArea = document.getElementById('notes-textarea');

    // --- Sanity check ---
    if (!htmlCode || !preview) {
        console.error("Critical elements missing: html-code or preview.");
        return;
    }

    // --- Load the welcome template into the editor ---
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
</html>
    `.trim();

    // --------------------------------------------------
    // ⚙️ Initialize Features
    // --------------------------------------------------
    try {
        // Initialize preview system
        await initPreview(htmlCode, preview, slug);

        // AI-assisted generation
        initAiGeneration(htmlCode, updatePreview,notesArea);

        // File management (save/load)
        setupFileHandlers(htmlCode, updatePreview);

        // Deployment hooks
        setupDeployment(htmlCode, slug);

        // Form integration (the settings sidebar)
        await initFormGeneration(sidebar, toggleBtn, formSelect, loadBtn, notesArea);

        // Visual/UX effects
        setupEffects();

        console.log("✅ All systems initialized successfully!");
    } catch (err) {
        console.error("Initialization error:", err);
    }
});
