// 1. Import Alpine and Plugins
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/module.esm.js';
import sort from 'https://cdn.jsdelivr.net/npm/@alpinejs/sort@latest/dist/module.esm.js'; 

// 4. App Logic
import { HikarinApi } from '../hikarin/api/client.js';
import editorManager from './alpine/editorManager.js';


// --- Alpine Setup ---
const hikarinApi = new HikarinApi();

Alpine.plugin(sort);
Alpine.magic('api', () => hikarinApi);

Alpine.store('notifications', {
    items: [],
    add(notification) {
        const id = Date.now();
        this.items.push({ ...notification, id });
        setTimeout(() => {
            this.items = this.items.filter(i => i.id !== id);
        }, 3000);
    }
});

Alpine.data('editorManager', editorManager);

window.Alpine = Alpine;
Alpine.start();

console.log("Hikarin JS (Clean Load): Started");