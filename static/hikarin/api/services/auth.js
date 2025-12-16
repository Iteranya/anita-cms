import { ApiRequest } from "../core.js";

export class AuthAPI {
    constructor(client) {
        this._client = client;
    }

    // ------------------
    // LOGIN
    // ------------------

    login(username, password, rememberMe = false) {
        return new ApiRequest(() => {
            const fd = new FormData();
            fd.append("username", username);
            fd.append("password", password);
            fd.append("remember_me", String(rememberMe));

            return this._client._request("POST", "/auth/login", {
                body: fd
            });
        });
    }

    logout() {
        return new ApiRequest(() =>
            this._client._request("POST", "/auth/logout")
        );
    }

    // ------------------
    // SETUP
    // ------------------

    checkSetup() {
        return new ApiRequest(() =>
            this._client._request("GET", "/auth/check-setup")
        );
    }

    setupAdmin(username, password, confirmPassword) {
        return new ApiRequest(() => {
            const fd = new FormData();
            fd.append("username", username);
            fd.append("password", password);
            fd.append("confirm_password", confirmPassword);

            return this._client._request("POST", "/auth/setup", {
                body: fd
            });
        });
    }

    // ------------------
    // REGISTRATION
    // ------------------

    register(username, password, confirmPassword, displayName = null) {
        return new ApiRequest(() => {
            const fd = new FormData();
            fd.append("username", username);
            fd.append("password", password);
            fd.append("confirm_password", confirmPassword);

            if (displayName) {
                fd.append("display_name", displayName);
            }

            return this._client._request("POST", "/auth/register", {
                body: fd
            });
        });
    }
}
