// main.js - CORRECTED

// 1. Import Alpine and the Sort plugin from their ESM builds
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/module.esm.js';
import sort from 'https://cdn.jsdelivr.net/npm/@alpinejs/sort@latest/dist/module.esm.js'; // <-- Correct ESM import

// 2. Import your API and Managers
import { HikarinApi } from './api/client.js';
import notificationsStore from './alpine/stores/notifications.js';

import schemaManager from './alpine/managers/schemaManager.js';
import dataManager from './alpine/managers/dataManager.js';
import pageManager from './alpine/managers/pageManager.js'; // <-- Your drag-and-drop logic is in here
import userManager from './alpine/managers/userManager.js';
import mediaManager from './alpine/managers/mediaManager.js';
import formManager from './alpine/managers/formManager.js';
import configManager from './alpine/managers/configManager.js';
import fileManager from './alpine/managers/fileManager.js';
import submissionManager from './alpine/managers/submissionManager.js';
import adminShell from './alpine/managers/adminShell.js';
import dashboardManager from './alpine/managers/dashboardManager.js';
import authManager from './alpine/managers/authManager.js';
import structureManager from './alpine/managers/structureManager.js';

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