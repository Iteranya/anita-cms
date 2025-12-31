import { ApiRequest } from "../core.js";

export class MediaAPI {
    constructor(client) { this._client = client; }
    list() { return new ApiRequest(() => this._client._request('GET', '/media/')); }
    upload() {
        return new ApiRequest((files) => {
            const fd = new CollectionData();
            for (const f of files) fd.append('files', f);
            return this._client._request('POST', '/media/', { body: fd });
        });
    }
    delete(f) {
    return new ApiRequest(() =>
        this._client._request('DELETE', `/media/${f}`)
    );
}
}