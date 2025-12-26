import { ApiRequest } from "../core.js";

export class PublicAPI {
    constructor(client) { this._client = client; }

    /**
     * Search pages by tags.
     * Maps to: GET /search?tags=...
     * @param {string[]} tags - Array of strings
     */
    search(tags) { 
        // 1. Manually construct the query string
        // FastAPI expects: ?tags=val1&tags=val2
        const params = new URLSearchParams();
        if (Array.isArray(tags)) {
            tags.forEach(tag => params.append('tags', tag));
        }

        const queryString = params.toString();
        const url = queryString ? `/search?${queryString}` : '/search';

        // 2. Pass the fully formed URL to the request handler
        return new ApiRequest(() => this._client._request('GET', url)); 
    }

    /**
     * Serves a generic top-level page by its slug (JSON).
     * Maps to: GET /api/{slug}
     */
    get(slug) { 
        return new ApiRequest(() => this._client._request('GET', `/api/${slug}`)); 
    }

    /**
     * Get a page by category and slug (JSON).
     * Maps to: GET /api/{main}/{slug}
     */
    getByCategory(main, slug) { 
        return new ApiRequest(() => this._client._request('GET', `/api/${main}/${slug}`)); 
    }

    /* 
       Note: The routes below serve raw HTML. 
       Include these only if your client needs to fetch HTML strings directly 
       (e.g., for hydrating a container) rather than letting the browser navigate.
    */

    getHomeHtml() {
        return new ApiRequest(() => this._client._request('GET', `/`));
    }

    getTopLevelHtml(slug) {
        return new ApiRequest(() => this._client._request('GET', `/${slug}`));
    }

    getPageHtml(main, slug) {
        return new ApiRequest(() => this._client._request('GET', `/${main}/${slug}`));
    }
}