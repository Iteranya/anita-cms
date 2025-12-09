/**
 * HikarinSDK - Safe Bridge for AI-Generated Websites
 * 
 * This module provides a strict interface to the backend API.
 * It is designed to be injected into Alpine.js contexts.
 */

class HikarinClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    /**
     * Core request handler. 
     * Handles JSON encoding, credentials (cookies), and standard error parsing.
     */
    async _req(endpoint, method = 'GET', body = null, isMultipart = false) {
        const options = {
            method,
            headers: {},
            credentials: 'include', // Vital: Sends the HttpOnly access_token cookie
        };

        if (!isMultipart) {
            options.headers['Content-Type'] = 'application/json';
            options.headers['Accept'] = 'application/json';
            if (body) options.body = JSON.stringify(body);
        } else {
            // Let browser set Content-Type for FormData (multipart boundaries)
            options.body = body;
        }

        try {
            const res = await fetch(`${this.baseUrl}${endpoint}`, options);
            
            // specific handling for 204 No Content
            if (res.status === 204) return null;

            if (!res.ok) {
                // Try to parse error message from FastAPI
                let errorMsg = res.statusText;
                try {
                    const errorData = await res.json();
                    errorMsg = errorData.detail || errorMsg;
                } catch (e) {}
                throw new Error(errorMsg);
            }

            // Return blob for files/images if content-type isn't json
            const contentType = res.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") === -1) {
                return res.blob();
            }

            return await res.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error; 
        }
    }

    // ==========================================
    // 📄 PAGES
    // ==========================================
    pages = {
        /**
         * List pages. 
         * @param {string} tag - Optional filter by tag
         */
        list: async (tag = null) => {
            // Note: The backend route /page/list doesn't explicitly take a tag query param in your code
            // but the Public API /api/blog does. Let's support the generic list.
            return this._req(`/page/list`);
        },
        
        /** Get public blog posts */
        listBlog: async () => {
            return this._req(`/api/blog`);
        },

        get: async (slug) => {
            return this._req(`/page/${slug}`);
        },

        /** Get specific public blog post */
        getBlogPost: async (slug) => {
            return this._req(`/api/blog/${slug}`);
        }
    };

    // ==========================================
    // 📨 FORMS
    // ==========================================
    forms = {
        get: async (slug) => {
            return this._req(`/forms/${slug}`);
        },

        /**
         * Submit a form.
         * The backend expects: { data: {...}, custom: {...} }
         */
        submit: async (slug, formData, customData = {}) => {
            const payload = {
                data: formData,
                custom: customData
            };
            return this._req(`/forms/${slug}/submit`, 'POST', payload);
        }
    };

    // ==========================================
    // 👤 AUTH (Used for Login UI)
    // ==========================================
    auth = {
        login: async (username, password, rememberMe = false) => {
            // Login endpoint expects FormData, not JSON
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            formData.append('remember_me', rememberMe);
            
            // We use _req directly but override body for multipart/form
            return this._req('/auth/login', 'POST', formData, true);
        },
        
        logout: async () => {
            return this._req('/auth/logout', 'POST');
        },

        register: async (username, password, confirmPassword, displayName) => {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            formData.append('confirm_password', confirmPassword);
            if(displayName) formData.append('display_name', displayName);
            
            return this._req('/auth/register', 'POST', formData, true);
        }
    };

    // ==========================================
    // 📸 MEDIA & FILES
    // ==========================================
    media = {
        list: async () => {
            return this._req('/media/');
        },
        
        /**
         * Upload files.
         * @param {FileList | File[]} files 
         */
        upload: async (files) => {
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }
            return this._req('/media/', 'POST', formData, true);
        }
    };
    
    // ==========================================
    // ⚙️ UTILS
    // ==========================================
    utils = {
        /**
         * Helper to format dates from ISO string
         */
        formatDate: (isoString) => {
            if (!isoString) return '';
            return new Date(isoString).toLocaleDateString();
        }
    };
}

// Initialize and Export for Alpine
const sdk = new HikarinClient();

// Alpine Initialization
document.addEventListener('alpine:init', () => {
    // 1. Expose as a Magic Property ($api)
    // Usage: <button @click="$api.forms.submit(...)">
    Alpine.magic('api', () => sdk);

    // 2. Expose as a global object (optional, for non-Alpine scripts if any)
    window.HikarinSDK = sdk;
    
    // 3. Optional: Create a global store for User State
    Alpine.store('auth', {
        user: null,
        isLoggedIn: false,
        
        async checkStatus() {
            // You might need a specific endpoint to check "me" 
            // Currently using a try/catch on a protected route or dedicated /me endpoint
            // Since your API is cookie based, simple presence of functionality implies auth
        }
    });
});