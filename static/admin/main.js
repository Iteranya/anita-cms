
// 1. Import Alpine and the Sort plugin from their ESM builds
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/module.esm.js';
import sort from 'https://cdn.jsdelivr.net/npm/@alpinejs/sort@latest/dist/module.esm.js'; // <-- Correct ESM import

// 2. Import your API and Managers
import { HikarinApi } from '../hikarin/api/client.js';
import notificationsStore from '../hikarin/alpine/notifications.js'
import schemaManager from './alpine/schemaManager.js';
import dataManager from './alpine/dataManager.js';
import pageManager from './alpine/pageManager.js'; 
import userManager from './alpine/userManager.js';
import mediaManager from './alpine/mediaManager.js';
import formManager from './alpine/formManager.js';
import configManager from './alpine/configManager.js';
import fileManager from './alpine/fileManager.js';
import submissionManager from './alpine/submissionManager.js';
import adminShell from './alpine/adminShell.js';
import dashboardManager from './alpine/dashboardManager.js';
import structureManager from './alpine/structureManager.js';

// 3. Initialize API
const hikarinApi = new HikarinApi();

// 4. Register the Sort plugin with Alpine
// This MUST be done before Alpine.start()
Alpine.plugin(sort);

// 5. Register Magic & Store
Alpine.magic('api', () => hikarinApi);
Alpine.store('notifications', notificationsStore);

// 6. Register Components (x-data providers)
Alpine.data('schemaManager', schemaManager);
Alpine.data('dataManager', dataManager);
Alpine.data('pageManager', pageManager);
Alpine.data('structureManager', structureManager)
Alpine.data('userManager', userManager);
Alpine.data('mediaManager', mediaManager);
Alpine.data('formManager', formManager);
Alpine.data('configManager', configManager);
Alpine.data('fileManager', fileManager);
Alpine.data('submissionManager', submissionManager);
Alpine.data('dashboardManager',dashboardManager)
Alpine.data('authManager',authManager)
Alpine.data('adminShell', adminShell);

// 7. Make Alpine available globally (optional, for debugging)
window.Alpine = Alpine;

// 8. START ALPINE
// This single call initializes Alpine and all registered plugins.
Alpine.start();

console.log("Hikarin JS: Modules loaded and Alpine started correctly.");