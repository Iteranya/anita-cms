import { ApiRequest } from "../core.js";

/**
 * Client for interacting with the Dashboard API endpoints.
 */
export class DashboardAPI {
    constructor(client) {
        this._client = client;
    }

    /**
     * Retrieves aggregated statistics for the admin dashboard.
     * Corresponds to: GET /dashboard/stats
     */
    stats() {
        return new ApiRequest(() => this._client._request('GET', '/dashboard/stats'));
    }

    /**
     * Retrieves the profile of the currently authenticated user.
     * Corresponds to: GET /dashboard/me
     */
    me() {
        return new ApiRequest(() => this._client._request('GET', '/dashboard/me'));
    }

    /**
     * Updates the profile of the currently authenticated user.
     * Corresponds to: PUT /dashboard/me
     * @param {object} data - The user update payload (e.g., { display_name, pfp_url }).
     */
    updateMe() {
        return new ApiRequest((data) => this._client._request('PUT', '/dashboard/me', { body: data }));
    }
}