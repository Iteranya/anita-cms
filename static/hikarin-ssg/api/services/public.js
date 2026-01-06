import { ApiRequest } from "../core.js";

export class PublicAPI {
    constructor(client) { this._client = client; }

    /**
     * Search pages by labels.
     * Maps to: GET /search?labels=...
     * @param {string[]} labels - Array of strings
     */
    search(labels) { 
        // 1. Manually construct the query string
        const params = new URLSearchParams();
        if (Array.isArray(labels)) {
            labels.forEach(label => params.append('labels', label));
        }

        const queryString = params.toString();
        const url = queryString ? `/search?${queryString}` : '/search';

        // 2. Pass the fully formed URL to the request handler
        return new ApiRequest(() => this._client._request('GET', url)); 
    }

    get(slug) { 
        return new ApiRequest(() => this._client._request('GET', `/api/${slug}`)); 
    }

    getByCategory(main, slug) { 
        return new ApiRequest(() => this._client._request('GET', `/api/${main}/${slug}`)); 
    }

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