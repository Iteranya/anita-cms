import { ApiRequest } from "../core.js";

export class AuthAPI {
    constructor(client) { 
        this._client = client; 
    }
    
    login(u, p, r=false) {
        return new ApiRequest(async () => {
            const fd = new FormData();
            fd.append('username', u); 
            fd.append('password', p); 
            fd.append('remember_me', String(r));
            
            const response = await this._client._request('POST', '/auth/login', { body: fd });
            
            // Save CSRF token to localStorage
            if (response.csrf_token) {
                this._client.setCsrfToken(response.csrf_token);
            }
            
            return response;
        });
    }
    
    logout() { 
        return new ApiRequest(async () => {
            const response = await this._client._request('POST', '/auth/logout');
            
            // Clear CSRF token from localStorage
            this._client.setCsrfToken(null);
            
            return response;
        });
    }
}