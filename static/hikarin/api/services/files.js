import { ApiRequest } from "../core.js";

export class FileAPI {
    constructor(client) { this._client = client; }

    // POST /file/
    // Expects a single File object (from input.files[0])
    upload() {
        return new ApiRequest((fileObj) => {
            const fd = new FormData();
            fd.append('file', fileObj); 
            return this._client._request('POST', '/file/', { body: fd });
        });
    }

    // DELETE /file/{filename}
    delete(filename) { 
        return new ApiRequest(() => this._client._request('DELETE', `/file/${filename}`)); 
    }
}