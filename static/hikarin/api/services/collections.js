import { ApiRequest } from "../core.js";

export class CollectionsAPI {
    constructor(client) { this._client = client; }
    
    list(label=null) { 
        const q = label ? `?label=${label}` : '';
        return new ApiRequest(() => this._client._request('GET', `/forms/list${q}`)); 
    }
    get(slug) { return new ApiRequest(() => this._client._request('GET', `/forms/${slug}`)); }
    create(data) { return new ApiRequest(() => this._client._request('POST', '/forms/', { body: data })); }
    update(slug, data) { return new ApiRequest(() => this._client._request('PUT', `/forms/${slug}`, { body: data })); }
    delete(slug) { return new ApiRequest(() => this._client._request('DELETE', `/forms/${slug}`)); }
    
    listRecords(slug, skip=0, limit=100) {
        return new ApiRequest(() => this._client._request('GET', `/forms/${slug}/submissions?skip=${skip}&limit=${limit}`));
    }
    createRecord(slug, payload) {
        return new ApiRequest(() => this._client._request('POST', `/forms/${slug}/submit`, { body: payload }));
    }
    updateRecord(slug, id, payload) {
        return new ApiRequest(() => this._client._request('PUT', `/forms/${slug}/submissions/${id}`, { body: payload }));
    }
    deleteRecord(slug, id) {
        return new ApiRequest(() => this._client._request('DELETE', `/forms/${slug}/submissions/${id}`));
    }
}