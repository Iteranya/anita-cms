// file: static/js/hikarin-api.js

/**
 * Custom Error for API responses that are not successful.
 * Contains the HTTP status code for better handling in UI components.
 */
class HikarinApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = 'HikarinApiError';
        this.status = status;
    }
}

/**
 * The HikarinAPI Client for the browser.
 * This class organizes all API calls into logical groups (auth, pages, forms, etc.)
 * to be used by Alpine.js components.
 */
class HikarinApi {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

        this.auth = new AuthAPI(this);
        this.config = new ConfigAPI(this);
        this.forms = new FormsAPI(this);
        this.media = new MediaAPI(this);
        this.pages = new PagesAPI(this);
        this.public = new PublicAPI(this);
        this.users = new UsersAPI(this);
    }

    /**
     * The core request method. Handles JSON/FormData, errors, and auth.
     */
    async _request(method, endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = { method: method.toUpperCase(), headers: {}, ...options };

        if (options.body) {
            if (options.body instanceof FormData) {
                config.body = options.body;
            } else {
                config.headers['Content-Type'] = 'application/json';
                config.body = JSON.stringify(options.body);
            }
        }

        const response = await fetch(url, config);

        if (!response.ok) {
            let errorMessage = `API Error: ${response.status}`;
            try {
                const errorBody = await response.json();
                errorMessage = errorBody.detail || JSON.stringify(errorBody);
            } catch (e) { /* Response body might not be JSON */ }
            throw new HikarinApiError(errorMessage, response.status);
        }

        if (response.status === 204) return null;
        if (options.rawResponse) return response;
        return response.json();
    }
}

// ===================================================================
//  API Resource Classes
// ===================================================================

class AuthAPI {
    constructor(client) { this._client = client; }
    login(username, password, rememberMe = false) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('remember_me', String(rememberMe));
        return this._client._request('POST', '/auth/login', { body: formData });
    }
    logout() { return this._client._request('POST', '/auth/logout'); }
    setupAdmin(username, password, confirmPassword) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('confirm_password', confirmPassword);
        return this._client._request('POST', '/auth/setup', { body: formData });
    }
    checkSetup() { return this._client._request('GET', '/auth/check-setup'); }
    register(username, password, confirmPassword, displayName) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('confirm_password', confirmPassword);
        if (displayName) formData.append('display_name', displayName);
        return this._client._request('POST', '/auth/register', { body: formData });
    }
}

class ConfigAPI {
    constructor(client) { this._client = client; }
    get() { return this._client._request('GET', '/config/'); }
    update(configData) { return this._client._request('POST', '/config/', { body: configData }); }
}

class PagesAPI {
    constructor(client) { this._client = client; }
    create(pageData) { return this._client._request('POST', '/page/', { body: pageData }); }
    list({ skip = 0, limit = 100 } = {}) {
        const params = new URLSearchParams({ skip, limit });
        return this._client._request('GET', `/page/list?${params.toString()}`);
    }
    get(slug) { return this._client._request('GET', `/page/${slug}`); }
    update(slug, updateData) { return this._client._request('PUT', `/page/${slug}`, { body: updateData }); }
    delete(slug) { return this._client._request('DELETE', `/page/${slug}`); }
}

class FormsAPI {
    constructor(client) { this._client = client; }
    create(formData) { return this._client._request('POST', '/forms/', { body: formData }); }
    list({ tag, skip = 0, limit = 100 } = {}) {
        const params = new URLSearchParams({ skip, limit });
        if (tag) params.append('tag', tag);
        return this._client._request('GET', `/forms/list?${params.toString()}`);
    }
    get(slug) { return this._client._request('GET', `/forms/${slug}`); }
    update(slug, updateData) { return this._client._request('PUT', `/forms/${slug}`, { body: updateData }); }
    delete(slug) { return this._client._request('DELETE', `/forms/${slug}`); }
    getAllTags() { return this._client._request('GET', '/forms/tags/all'); }
    submissions(formSlug) { return new SubmissionsAPI(this._client, formSlug); }
}

class SubmissionsAPI {
    constructor(client, formSlug) {
        this._client = client;
        this.basePath = `/forms/${formSlug}`;
    }
    submit(data, custom = {}) {
        return this._client._request('POST', `${this.basePath}/submit`, { body: { data, custom } });
    }
    list({ skip = 0, limit = 100 } = {}) {
        const params = new URLSearchParams({ skip, limit });
        return this._client._request('GET', `${this.basePath}/submissions?${params.toString()}`);
    }
    get(submissionId) { return this._client._request('GET', `${this.basePath}/submissions/${submissionId}`); }
    update(submissionId, updateData) { return this._client._request('PUT', `${this.basePath}/submissions/${submissionId}`, { body: updateData }); }
    delete(submissionId) { return this._client._request('DELETE', `${this.basePath}/submissions/${submissionId}`); }
}

class MediaAPI {
    constructor(client) { this._client = client; }
    list() { return this._client._request('GET', '/media/'); }
    get(filename) { return this._client._request('GET', `/media/${filename}`, { rawResponse: true }); }
    upload(files) {
        const formData = new FormData();
        for (const file of files) formData.append('files', file);
        return this._client._request('POST', '/media/', { body: formData });
    }
    delete(filename) { return this._client._request('DELETE', `/media/${filename}`); }
}

class PublicAPI {
    constructor(client) { this._client = client; }
    listBlogPosts() { return this._client._request('GET', '/api/blog'); }
    getBlogPost(slug) { return this._client._request('GET', `/api/blog/${slug}`); }
}

class UsersAPI {
    constructor(client) { this._client = client; }
    list() { return this._client._request('GET', '/users/'); }
    create(userData) { return this._client._request('POST', '/users/', { body: userData }); }
    update(username, updateData) { return this._client._request('PUT', `/users/${username}`, { body: updateData }); }
    changePassword(username, newPassword) {
        return this._client._request('PUT', `/users/${username}/password`, { body: { new_password: newPassword } });
    }
    delete(username) { return this._client._request('DELETE', `/users/${username}`); }
    roles() { return new RolesAPI(this._client); }
}

class RolesAPI {
    constructor(client) { this._client = client; }
    list() { return this._client._request('GET', '/users/roles'); }
    save(roleName, permissions) {
        return this._client._request('POST', '/users/roles', { body: { role_name: roleName, permissions } });
    }
    delete(roleName) { return this._client._request('DELETE', `/users/roles/${roleName}`); }
}

// ===================================================================
//  ALPINE.JS INTEGRATION - The CSP-Compliant "Glue"
// ===================================================================

// 1. Instantiate the single client instance for the entire application.
const hikarinApi = new HikarinApi();

// 2. Wait for Alpine to initialize, then register our client.
document.addEventListener('alpine:init', () => {
    Alpine.magic('api', () => hikarinApi);
});