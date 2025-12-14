export class HikarinApiError extends Error {
    constructor(message, status, detail) {
        super(message);
        this.name = 'HikarinApiError';
        this.status = status;
        this.detail = detail;
    }
}

export class ApiRequest {
    constructor(apiCall) {
        this._apiCall = apiCall;
        this.data = null;
        this.error = null;
        this.loading = false;
        this.called = false;
    }
    async execute(...args) {
        this.loading = true;
        this.error = null;
        this.called = true;
        try {
            const result = await this._apiCall(...args);
            this.data = result;
            return result;
        } catch (e) {
            this.error = e;
            throw e;
        } finally {
            this.loading = false;
        }
    }
    get isLoading() { return this.loading; }
    get isSuccess() { return this.called && !this.loading && !this.error; }
}