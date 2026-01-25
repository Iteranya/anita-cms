import { ApiRequest } from "../core.js";

// TODO: Turn this into true SSG

export class CollectionsAPI {
    constructor(client) { this._client = client; }
    
    list(label=null) { 
        const q = label ? `?label=${label}` : '';
        return new ApiRequest(() => this._client._request('GET', `/collections/list${q}`)); 
    }
    get(slug) { return new ApiRequest(() => this._client._request('GET', `/collections/${slug}`)); }
    create(data) { return new ApiRequest(() => this._client._request('POST', '/collections/', { body: data })); }
    update(slug, data) { return new ApiRequest(() => this._client._request('PUT', `/collections/${slug}`, { body: data })); }
    delete(slug) { return new ApiRequest(() => this._client._request('DELETE', `/collections/${slug}`)); }
    
    listRecords(slug, skip=0, limit=100) {
        return new ApiRequest(() => this._client._request('GET', `/collections/${slug}/submissions?skip=${skip}&limit=${limit}`));
    }
    createRecord(slug, payload) {
        return new ApiRequest(() => this._client._request('POST', `/collections/${slug}/submit`, { body: payload }));
    }
    updateRecord(slug, id, payload) {
        return new ApiRequest(() => this._client._request('PUT', `/collections/${slug}/submissions/${id}`, { body: payload }));
    }
    deleteRecord(slug, id) {
        return new ApiRequest(() => this._client._request('DELETE', `/collections/${slug}/submissions/${id}`));
    }
}