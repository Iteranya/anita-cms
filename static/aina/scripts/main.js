// main.js - Entry point
import { initPreview } from './previewManager.js';
import { initAiGeneration } from './aiIntegration.js';
import { setupFileHandlers } from './fileHandler.js';
import { setupDeployment } from './deploymentService.js';
import { initSettingsManager } from './settingsManager.js';
import { setupEffects } from './effects.js';

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the HTML editor and preview
    const htmlCode = document.getElementById('html-code');
    const preview = document.getElementById('preview');
    
    // Initialize welcome message
    const welcomeHTML = `
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
    `;
    
    htmlCode.value = welcomeHTML;
    
    // Initialize all modules
    initPreview(htmlCode, preview);
    initAiGeneration(htmlCode, updatePreview);
    setupFileHandlers(htmlCode, updatePreview);
    setupDeployment(htmlCode);
    //initSettingsManager();
    setupEffects();
    
    // // FAB event listener
    // document.getElementById("fab").addEventListener("click", function() {
    //     var panel = document.getElementById("settings-panel");
    //     panel.style.display = panel.style.display === "none" || panel.style.display === "" ? "block" : "none";
    // });
    
    // // Close modal when clicking outside
    // window.addEventListener('click', function(event) {
    //     const modal = document.getElementById('deploy-modal');
    //     if (event.target === modal) {
    //         modal.style.display = 'none';
    //     }
    // });
});

// Import and expose updatePreview for modules that need it
import { updatePreview } from './previewManager.js';
export { updatePreview };