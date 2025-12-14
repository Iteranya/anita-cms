import { ApiRequest } from "../core.js";

export class AuthAPI {
    constructor(client) { this._client = client; }
    login(u, p, r=false) {
        return new ApiRequest(() => {
            const fd = new FormData();
            fd.append('username', u); fd.append('password', p); fd.append('remember_me', String(r));
            return this._client._request('POST', '/auth/login', { body: fd });
        });
    }
    logout() { return new ApiRequest(() => this._client._request('POST', '/auth/logout')); }
}