import { HikarinApiError } from './core.js';
import { AuthAPI } from './services/auth.js';
import { ConfigAPI } from './services/config.js';
import { CollectionsAPI } from './services/collections.js';
import { MediaAPI } from './services/media.js';
import { PagesAPI } from './services/pages.js';
import { UsersAPI } from './services/users.js';
import { FileAPI } from './services/files.js';
import { DashboardAPI } from './services/dashboard.js';
import { PublicAPI } from './services/public.js';
import { AinaAPI } from './services/aina.js';
import { AstaAPI } from './services/asta.js';

export class HikarinApi {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
        this._request = this._request.bind(this);
        this.auth = new AuthAPI(this);
        this.config = new ConfigAPI(this);
        this.collections = new CollectionsAPI(this);
        this.media = new MediaAPI(this);
        this.pages = new PagesAPI(this);
        this.users = new UsersAPI(this);
        this.files = new FileAPI(this); 
        this.dashboard = new DashboardAPI(this);
        this.public = new PublicAPI(this);
        this.aina = new AinaAPI(this);
        this.asta = new AstaAPI(this);
        
    }

    _getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async _request(method, endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        
        const config = {
            method: method.toUpperCase(),
            headers: {},
            credentials: 'include',
            ...options
        };

        if (options.body && !(options.body instanceof FormData)) {
            config.headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(options.body);
        }
        if (!(options.body instanceof FormData)) config.headers['Accept'] = 'application/json';

        const safeMethods = ['GET', 'HEAD', 'OPTIONS', 'TRACE'];
        if (!safeMethods.includes(config.method)) {
            
            const csrfToken = this._getCookie('fastapi-csrf-token');
            if (csrfToken) {
                console.log(csrfToken)
                config.headers['X-CSRF-Token'] = csrfToken;
            } else {
                // This can happen if the user's first action is a POST before visiting a page
                // that sets the cookie. The backend will correctly reject this.
                console.warn('CSRF token cookie not found. The request may be rejected.');
            }
        }

        const response = await fetch(url, config);
        
        if (!response.ok) {
            let errorDetail = null;
            let errorMessage = `API Error: ${response.statusText}`;
            try {
                const body = await response.json();
                errorDetail = body;
                errorMessage = body.detail || errorMessage;
            } catch (e) {}
            throw new HikarinApiError(errorMessage, response.status, errorDetail);
        }
        
        if (response.status === 204) return null;
        
        const contentType = response.headers.get('content-type');
        return (contentType && contentType.includes('application/json')) ? response.json() : response;
    }
}