// file: static/hikarin/hikarin.js

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
 * A stateful wrapper for an API call.
 * (This class is unchanged as its logic is independent of the request implementation)
 */
class ApiRequest {
    constructor(apiCall) {
        this._apiCall = apiCall;
        this.data = null;
        this.error = null;
        this.loading = false;
        this.called = false;
    }
    async execute(...args) {
        this.loading = true;
        this.error = null;
        this.called = true;
        try {
            const result = await this._apiCall(...args);
            this.data = result;
            return result;
        } catch (e) {
            this.error = e;
            throw e;
        } finally {
            this.loading = false;
        }
    }
    reset() {
        this.data = null;
        this.error = null;
        this.loading = false;
        this.called = false;
    }
    get isLoading() { return this.loading; }
    get isSuccess() { return this.called && !this.loading && !this.error; }
    get isError() { return !!this.error; }
}


/**
 * The HikarinAPI Client for the browser.
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
     * Reads a cookie value by its name.
     * Used internally to retrieve the CSRF token.
     * @param {string} name The name of the cookie.
     * @returns {string|null} The cookie value or null if not found.
     */
    _getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    /**
     * The core request method. Enhanced with security and smart response handling.
     */
    async _request(method, endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method: method.toUpperCase(),
            headers: {},
            // **SECURITY**: Always send cookies (for HttpOnly session tokens) with requests.
            credentials: 'include',
            ...options
        };

        const isStateChanging = !['GET', 'HEAD', 'OPTIONS'].includes(config.method);

        // Set content type and stringify body for JSON requests
        if (options.body && !(options.body instanceof FormData)) {
            config.headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(options.body);
        }

        // Set Accept header for non-FormData requests to signal we prefer JSON responses
        if (!(options.body instanceof FormData)) {
             config.headers['Accept'] = 'application/json';
        }

        // **SECURITY**: Automatically add CSRF token to state-changing requests.
        // Your backend must set a 'csrftoken' cookie for this to work.
        if (isStateChanging) {
            const csrfToken = this._getCookie('csrftoken');
            if (csrfToken) {
                config.headers['X-CSRF-Token'] = csrfToken;
            } else {
                console.warn(`HikarinAPI: CSRF token cookie 'csrftoken' not found. State-changing requests to ${endpoint} may be rejected.`);
            }
        }

        const response = await fetch(url, config);

        if (!response.ok) {
            let errorMessage = `API Error: ${response.statusText}`;
            try {
                const errorBody = await response.json();
                errorMessage = errorBody.detail || JSON.stringify(errorBody);
            } catch (e) { /* Response body might not be JSON or might be empty */ }
            throw new HikarinApiError(errorMessage, response.status);
        }

        if (response.status === 204) return null; // Handle No Content responses

        // **SMART RESPONSE**: Check content type. If not JSON, return the raw response
        // so the caller can handle it as a blob, text, etc.
        const contentType = response.headers.get('content-type');
        if (contentType && !contentType.includes('application/json')) {
            return response;
        }

        return response.json();
    }
}
// ===================================================================
//  API Resource Classes (Refactored to use ApiRequest)
// ===================================================================

class AuthAPI {
    constructor(client) { this._client = client; }
    login() {
        return new ApiRequest((username, password, rememberMe = false) => {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            formData.append('remember_me', String(rememberMe));
            return this._client._request('POST', '/auth/login', { body: formData });
        });
    }
    logout() { return new ApiRequest(() => this._client._request('POST', '/auth/logout')); }
    setupAdmin() {
        return new ApiRequest((username, password, confirmPassword) => {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            formData.append('confirm_password', confirmPassword);
            return this._client._request('POST', '/auth/setup', { body: formData });
        });
    }
    checkSetup() { return new ApiRequest(() => this._client._request('GET', '/auth/check-setup')); }
    register() {
        return new ApiRequest((username, password, confirmPassword, displayName) => {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            formData.append('confirm_password', confirmPassword);
            if (displayName) formData.append('display_name', displayName);
            return this._client._request('POST', '/auth/register', { body: formData });
        });
    }
}

class ConfigAPI {
    constructor(client) { this._client = client; }
    get() { return new ApiRequest(() => this._client._request('GET', '/config/')); }
    update() { return new ApiRequest((configData) => this._client._request('POST', '/config/', { body: configData })); }
}

class PagesAPI {
    constructor(client) { this._client = client; }
    create() { return new ApiRequest((pageData) => this._client._request('POST', '/page/', { body: pageData })); }
    list() {
        return new ApiRequest(({ skip = 0, limit = 100 } = {}) => {
            const params = new URLSearchParams({ skip, limit });
            return this._client._request('GET', `/page/list?${params.toString()}`);
        });
    }
    get() { return new ApiRequest((slug) => this._client._request('GET', `/page/${slug}`)); }
    update() { return new ApiRequest((slug, updateData) => this._client._request('PUT', `/page/${slug}`, { body: updateData })); }
    delete() { return new ApiRequest((slug) => this._client._request('DELETE', `/page/${slug}`)); }
}

class FormsAPI {
    constructor(client) { this._client = client; }
    create() { return new ApiRequest((formData) => this._client._request('POST', '/forms/', { body: formData })); }
    list() {
        return new ApiRequest(({ tag, skip = 0, limit = 100 } = {}) => {
            const params = new URLSearchParams({ skip, limit });
            if (tag) params.append('tag', tag);
            return this._client._request('GET', `/forms/list?${params.toString()}`);
        });
    }
    get() { return new ApiRequest((slug) => this._client._request('GET', `/forms/${slug}`)); }
    update() { return new ApiRequest((slug, updateData) => this._client._request('PUT', `/forms/${slug}`, { body: updateData })); }
    delete() { return new ApiRequest((slug) => this._client._request('DELETE', `/forms/${slug}`)); }
    getAllTags() { return new ApiRequest(() => this._client._request('GET', '/forms/tags/all')); }
    submissions(formSlug) { return new SubmissionsAPI(this._client, formSlug); }
}

class SubmissionsAPI {
    constructor(client, formSlug) {
        this._client = client;
        this.basePath = `/forms/${formSlug}`;
    }
    submit() { return new ApiRequest((data, custom = {}) => this._client._request('POST', `${this.basePath}/submit`, { body: { data, custom } })); }
    list() {
        return new ApiRequest(({ skip = 0, limit = 100 } = {}) => {
            const params = new URLSearchParams({ skip, limit });
            return this._client._request('GET', `${this.basePath}/submissions?${params.toString()}`);
        });
    }
    get() { return new ApiRequest((submissionId) => this._client._request('GET', `${this.basePath}/submissions/${submissionId}`)); }
    update() { return new ApiRequest((submissionId, updateData) => this._client._request('PUT', `${this.basePath}/submissions/${submissionId}`, { body: updateData })); }
    delete() { return new ApiRequest((submissionId) => this._client._request('DELETE', `${this.basePath}/submissions/${submissionId}`)); }
}

class MediaAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', '/media/')); }
    get() { return new ApiRequest((filename) => this._client._request('GET', `/media/${filename}`, { rawResponse: true })); }
    upload() {
        return new ApiRequest((files) => {
            const formData = new FormData();
            for (const file of files) formData.append('files', file);
            return this._client._request('POST', '/media/', { body: formData });
        });
    }
    delete() { return new ApiRequest((filename) => this._client._request('DELETE', `/media/${filename}`)); }
}

class PublicAPI {
    constructor(client) { this._client = client; }
    listBlogPosts() { return new ApiRequest(() => this._client._request('GET', '/api/blog')); }
    getBlogPost() { return new ApiRequest((slug) => this._client._request('GET', `/api/blog/${slug}`)); }
}

class UsersAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', '/users/')); }
    create() { return new ApiRequest((userData) => this._client._request('POST', '/users/', { body: userData })); }
    update() { return new ApiRequest((username, updateData) => this._client._request('PUT', `/users/${username}`, { body: updateData })); }
    changePassword() { return new ApiRequest((username, newPassword) => this._client._request('PUT', `/users/${username}/password`, { body: { new_password: newPassword } })); }
    delete() { return new ApiRequest((username) => this._client._request('DELETE', `/users/${username}`)); }
    roles() { return new RolesAPI(this._client); }
}

class RolesAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', '/users/roles')); }
    save() { return new ApiRequest((roleName, permissions) => this._client._request('POST', '/users/roles', { body: { role_name: roleName, permissions } })); }
    delete() { return new ApiRequest((roleName) => this._client._request('DELETE', `/users/roles/${roleName}`)); }
}

// ===================================================================
//  ALPINE.JS INTEGRATION (Unchanged)
// ===================================================================

const hikarinApi = new HikarinApi();
document.addEventListener('alpine:init', () => {
    Alpine.magic('api', () => hikarinApi);
});