import { ApiRequest } from "../core.js";

export class ConfigAPI {
    constructor(client) { this._client = client; }
    get() { return new ApiRequest(() => this._client._request('GET', '/config/')); }
    update() { return new ApiRequest((d) => this._client._request('POST', '/config/', { body: d })); }
}