// 1. Import Alpine and Plugins
import Alpine from 'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/module.esm.js';
import sort from 'https://cdn.jsdelivr.net/npm/@alpinejs/sort@latest/dist/module.esm.js';

// 2. Import Managers
import { HikarinApi } from '../hikarin/api/client.js';
import notificationsStore from '../hikarin/alpine/notifications.js';
import authShell from './alpine/authShell.js';
import authManager from './alpine/authManager.js';

// 3. Initialize API
const hikarinApi = new HikarinApi();

// 4. Register Plugins
Alpine.plugin(sort);

// 5. Register Magic & Store
Alpine.magic('api', () => hikarinApi);
Alpine.store('notifications', notificationsStore);

// 6. Register Components
Alpine.data('authManager', authManager);
Alpine.data('authShell', authShell);

// 7. Global Debugging (Optional)
window.Alpine = Alpine;

// 8. Start Alpine
Alpine.start();