import { ApiRequest } from "../core.js";

export class AinaAPI {
    constructor(client) {
        this._client = client;
    }

    get(slug) {
        return new ApiRequest(() =>
            this._client._request("GET", `/page/${slug}`)
        );
    }

    updateHTML() {
        return new ApiRequest((slug, data) =>
            this._client._request("PUT", `/page/${slug}/html`, {
                body: data,
            })
        );
    }

    getRoutes(){
        return new ApiRequest(() =>
            this._client._request("GET",`/aina/routes`,{
            })
        );
    }
}
