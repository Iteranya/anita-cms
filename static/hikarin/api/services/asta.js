import { ApiRequest } from "../core.js";

export class AstaAPI {
    constructor(client) {
        this._client = client;
    }

    get(slug) {
        return new ApiRequest(() =>
            this._client._request("GET", `/page/${slug}`)
        );
    }

    updateMarkdown() {
        return new ApiRequest((slug, data) =>
            this._client._request("PUT", `/page/${slug}/markdown`, {
                body: data,
            })
        );
    }

    getEmbeds(){
        return new ApiRequest(() =>
            this._client._request("GET",`/asta/routes`,{
            })
        );
    }

    upload() {
        return new ApiRequest((files) => {
            const fd = new CollectionData();
            for (const f of files) fd.append('files', f);
            return this._client._request('POST', '/media/', { body: fd });
        });
    }
}
