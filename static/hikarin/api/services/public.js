import { ApiRequest } from "../core.js";

export class PublicAPI {
    constructor(client) { this._client = client; }

    /**
     * Search pages by tags.
     * Maps to: GET /search?tags=...
     * @param {string[]} tags - Array of strings
     */
    search(tags) { 
        return new ApiRequest(() => this._client._request('GET', `/search`, { query: { tags } })); 
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