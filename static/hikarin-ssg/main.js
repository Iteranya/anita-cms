
// 1. Import Alpine and the Sort plugin from their ESM builds
import Alpine from './lib/alpine.js';
import sort from './lib/alpine-sort.js'; // <-- Correct ESM import

// 2. Import your API and Managers
import { HikarinApi } from './api/client.js';
import notificationsStore from './alpine/notifications.js'

// 3. Initialize API
const hikarinApi = new HikarinApi();

// 4. Register the Sort plugin with Alpine
// This MUST be done before Alpine.start()
Alpine.plugin(sort);

// 5. Register Magic & Store
Alpine.magic('api', () => hikarinApi);
Alpine.store('notifications', notificationsStore);

// 6. Register Components (x-data providers)

// 7. Make Alpine available globally (optional, for debugging)
window.Alpine = Alpine;

// 8. START ALPINE
// This single call initializes Alpine and all registered plugins.
Alpine.start();

console.log("Hikarin JS: Modules loaded and Alpine started correctly.");