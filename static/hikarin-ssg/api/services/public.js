import { ApiRequest, HikarinApiError } from "../core.js";

export class PublicAPI {
    constructor(client) {
        this._client = client;
        this._dataPromise = null; // Cache for the JSON fetch
    }

    /**
     * Fetches and caches pages.json.
     * @returns {Promise<Array>} List of page objects
     */
    async _getDb() {
        if (this._dataPromise) return this._dataPromise;

        // 1. Resolve path relative to current script: dist/static/hikarin/api/services/public.js
        // 2. Go up 3 levels to: dist/static/
        // 3. Go down to: dist/static/data/pages.json
        const jsonUrl = new URL('../../../data/pages.json', import.meta.url).href;

        this._dataPromise = fetch(jsonUrl)
            .then(async (res) => {
                if (!res.ok) throw new Error(`Failed to load pages.json: ${res.statusText}`);
                return res.json();
            })
            .catch(err => {
                this._dataPromise = null; // Reset cache on error
                console.error(err); // Helpful for debugging SSG paths
                throw new HikarinApiError("Could not load static content.", 500, err);
            });
        
        return this._dataPromise;
    }

    /**
     * Helper to emulate Python's: required_labels.issubset(page.labels)
     */
    _checkLabels(page, requiredLabels) {
        if (!page.labels || !Array.isArray(page.labels)) return false;
        return requiredLabels.every(req => page.labels.includes(req));
    }

    /**
     * Helper to find a page and validate labels, mimicking backend 404s
     */
    async _findPage(predicate, requiredLabels) {
        const pages = await this._getDb();
        const page = pages.find(predicate);

        // 1. Page must exist
        if (!page) {
            throw new HikarinApiError("Page not found", 404);
        }

        // 2. Page must have required labels (Security/Category check)
        if (!this._checkLabels(page, requiredLabels)) {
            throw new HikarinApiError("Page not found in this category.", 404);
        }

        return page;
    }

    /**
     * Search pages by labels.
     * Logic: Returns pages containing ALL provided labels + "any:read"
     */
    search(labels = []) {
        return new ApiRequest(async () => {
            const pages = await this._getDb();
            
            // Backend logic: search_labels.append("any:read")
            const searchLabels = Array.isArray(labels) ? [...labels] : [];
            searchLabels.push("any:read");

            // Filter
            return pages.filter(page => this._checkLabels(page, searchLabels));
        });
    }

    /**
     * Mapped to: GET /api/{slug} AND GET /{slug}
     * Logic: Slug match + labels {"sys:head", "any:read"}
     */
    get(slug) {
        return new ApiRequest(() => 
            this._findPage(p => p.slug === slug, ["sys:head", "any:read"])
        );
    }

    /**
     * Mapped to: GET /api/{main}/{slug} AND GET /{main}/{slug}
     * Logic: Slug match + labels {f"main:{main}", "any:read"}
     */
    getByCategory(main, slug) {
        return new ApiRequest(() => 
            this._findPage(p => p.slug === slug, [`main:${main}`, "any:read"])
        );
    }

    /**
     * Mapped to: GET /
     * Logic: First page with labels ["sys:home", "any:read"]
     */
    getHomeHtml() {
        return new ApiRequest(async () => {
            const pages = await this._getDb();
            // Python: get_first_page_by_labels(['sys:home','any:read'])
            const required = ["sys:home", "any:read"];
            
            const page = pages.find(p => this._checkLabels(p, required));
            
            if (!page) throw new HikarinApiError("Critical: Home page not configured.", 404);
            return page;
        });
    }

    /**
     * SSG Equivalent: Returns the Page Object (JSON).
     * In an SSG context without a backend renderer, the 'HTML' methods
     * just return the data object found in pages.json.
     */
    getTopLevelHtml(slug) {
        return this.get(slug);
    }

    getPageHtml(main, slug) {
        return this.getByCategory(main, slug);
    }
}