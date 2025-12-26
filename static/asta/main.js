// main.js

// 1. Import Alpine and Plugins
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/module.esm.js';
import sort from 'https://cdn.jsdelivr.net/npm/@alpinejs/sort@latest/dist/module.esm.js'; 

// 2. Import Crepe (Milkdown) from esm.sh for browser compatibility
import { Crepe } from 'https://esm.sh/@milkdown/crepe@latest';

// 3. Import Your Logic (Kept exactly as is)
import { HikarinApi } from '../hikarin/api/client.js';
import notificationsStore from '../hikarin/alpine/notifications.js';
import astaShell from './alpine/astaShell.js';
import editorManager from './alpine/editorManager.js';
import settingManager from './alpine/settingManager.js'

// ==========================================
// CREPE (MILKDOWN) CONFIGURATION & SERVICE
// ==========================================

// Helper to inject Crepe CSS dynamically (since we aren't using a bundler like Vite/Webpack)
const injectCrepeStyles = () => {
    const themes = [
        "https://esm.sh/@milkdown/crepe@latest/theme/common/style.css",
        "https://esm.sh/@milkdown/crepe@latest/theme/frame.css"
    ];

    themes.forEach(url => {
        if (!document.querySelector(`link[href="${url}"]`)) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = url;
            document.head.appendChild(link);
        }
    });
};

// Global Helper to init Crepe editors cleanly in Alpine components
window.CrepeService = {
    // Config: Allow passing specific feature toggles or callbacks
    init: async (element, value, config = {}) => {
        
        // 1. Ensure CSS is loaded
        injectCrepeStyles();

        // 2. Configure Crepe
        const crepe = new Crepe({
            root: element,
            defaultValue: value || "",
            features: {
                [Crepe.Feature.Placeholder]: true,
                // You can disable features here if needed:
                // [Crepe.Feature.CodeMirror]: false, 
            },
            featureConfigs: {
                [Crepe.Feature.Placeholder]: {
                    text: 'Start writing your story...',
                },
                ...config.featureConfigs
            }
        });

        // 3. Create the editor instance
        await crepe.create();

        // 4. Setup Event Listeners (Syncing with Alpine)
        if (config.onChange) {
            crepe.on((listener) => {
                listener.markdownUpdated((markdown) => {
                    config.onChange(markdown);
                });
            });
        }

        // 5. Return the instance so Alpine can store it (to call .destroy(), .setReadonly(), etc.)
        return crepe;
    }
};

// ==========================================
// ALPINE SETUP
// ==========================================

const hikarinApi = new HikarinApi();

Alpine.plugin(sort);

Alpine.magic('api', () => hikarinApi);
Alpine.store('notifications', notificationsStore);
Alpine.store('astaState', {
    isSaving: false
});

Alpine.data('astaShell', astaShell);
Alpine.data('editorManager', editorManager);
Alpine.data('settingManager', settingManager);

// Make Alpine global for debugging
window.Alpine = Alpine;

Alpine.start();

console.log("Hikarin JS (Crepe Edition): Started");