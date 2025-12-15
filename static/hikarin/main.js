// 1. Import Alpine from the ESM (ES Module) CDN
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/module.esm.js';

// 2. Import your API and Managers
import { HikarinApi } from './api/client.js';
import notificationsStore from './alpine/stores/notifications.js';

import schemaManager from './alpine/managers/schemaManager.js';
import dataManager from './alpine/managers/dataManager.js';
import pageManager from './alpine/managers/pageManager.js';
import userManager from './alpine/managers/userManager.js';
import mediaManager from './alpine/managers/mediaManager.js';
import formManager from './alpine/managers/formManager.js';
import configManager from './alpine/managers/configManager.js';
import fileManager from './alpine/managers/fileManager.js';
import submissionManager from './alpine/managers/submissionManager.js';
import adminShell from './alpine/managers/adminShell.js';
import dashboardManager from './alpine/managers/dashboardManager.js';

// 3. Initialize API
const hikarinApi = new HikarinApi();

// 4. Register Magic & Store
// Note: We access Alpine directly now, not window.Alpine
Alpine.magic('api', () => hikarinApi);
Alpine.store('notifications', notificationsStore);

// 5. Register Components
Alpine.data('schemaManager', schemaManager);
Alpine.data('dataManager', dataManager);
Alpine.data('pageManager', pageManager);
Alpine.data('userManager', userManager);
Alpine.data('mediaManager', mediaManager);
Alpine.data('formManager', formManager);
Alpine.data('configManager', configManager);
Alpine.data('fileManager', fileManager);
Alpine.data('submissionManager', submissionManager);
Alpine.data('dashboardManager',dashboardManager)
Alpine.data('adminShell', adminShell);

// 6. Make Alpine available globally (optional, useful for debugging in console)
window.Alpine = Alpine;

// 7. START ALPINE
// This is the most important part. We start it manually only after everything is ready.
Alpine.start();

console.log("Hikarin JS: Modules loaded and Alpine started.");