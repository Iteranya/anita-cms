import { ApiRequest } from "../core.js";

export class UsersAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', '/users/')); }
    create() { return new ApiRequest((data) => this._client._request('POST', '/users/', { body: data })); }
    update(u, d) { return new ApiRequest(() => this._client._request('PUT', `/users/${u}`, { body: d })); }
    delete(u) { return new ApiRequest(() => this._client._request('DELETE', `/users/${u}`)); }
    roles() { return new ApiRequest(() => this._client._request('GET', '/users/roles')); }
}