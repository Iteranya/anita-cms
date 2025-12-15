import { HikarinApiError } from './core.js';
import { AuthAPI } from './services/auth.js';
import { ConfigAPI } from './services/config.js';
import { CollectionsAPI } from './services/collections.js';
import { MediaAPI } from './services/media.js';
import { PagesAPI } from './services/pages.js';
import { UsersAPI } from './services/users.js';
import { FileAPI } from './services/files.js';
import { DashboardAPI } from './services/dashboard.js';

export class HikarinApi {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
        
        // Load CSRF token from localStorage on init
        this.csrfToken = localStorage.getItem('fastapi-csrf-token');
        
        this.auth = new AuthAPI(this);
        this.config = new ConfigAPI(this);
        this.collections = new CollectionsAPI(this);
        this.media = new MediaAPI(this);
        this.pages = new PagesAPI(this);
        this.users = new UsersAPI(this);
        this.files = new FileAPI(this); 
        this.dashboard = new DashboardAPI(this);
    }

    /**
     * Set the CSRF token and persist to localStorage
     */
    setCsrfToken(token) {
        this.csrfToken = token;
        if (token) {
            localStorage.setItem('fastapi-csrf-token', token);
        } else {
            localStorage.removeItem('fastapi-csrf-token');
        }
    }

    /**
     * Get the current CSRF token
     */
    getCsrfToken() {
        return this.csrfToken;
    }

    async _request(method, endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method: method.toUpperCase(),
            headers: {},
            credentials: 'include',
            ...options
        };
        
        // --- CSRF Protection Logic ---
        const reqMethod = config.method.toUpperCase();
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(reqMethod)) {
            if (this.csrfToken) {
                config.headers['X-CSRF-Token'] = this.csrfToken;
            } else {
                console.warn(`CSRF token not found for a ${reqMethod} request to ${endpoint}. The request will likely fail.`);
            }
        }

        if (options.body && !(options.body instanceof FormData)) {
            config.headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(options.body);
        }
        if (!(options.body instanceof FormData)) config.headers['Accept'] = 'application/json';

        const response = await fetch(url, config);
        
        if (!response.ok) {
            let errorJson = null;
            let errorMessage = `API Error: ${response.statusText}`;
            try {
                errorJson = await response.json();
                errorMessage = errorJson.detail || errorMessage;
            } catch (e) {
                // If the body is not JSON, we just use the status text
            }
            throw new HikarinApiError(errorMessage, response.status, errorMessage); 
        }
        
        if (response.status === 204) return null;
        
        const contentType = response.headers.get('content-type');
        return (contentType && contentType.includes('application/json')) ? response.json() : response;
    }
}