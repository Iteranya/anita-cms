export default () => ({
    // --------------------
    // STATE
    // --------------------
    username: '',
    password: '',
    confirmPassword: '',
    displayName: '',
    rememberMe: false,

    loading: false,
    error: null,
    success: false,

    mode: 'login', // login | register | setup

    // --------------------
    // INIT
    // --------------------
    async init() {
        // Auto-detect setup state if relevant
        if (this.mode === 'login' || this.mode === 'register') {
            try {
                const res = await this.$api.auth.checkSetup().run();
                if (!res.initialized) {
                    window.location.href = '/auth/setup';
                }
            } catch (_) {}
        }
    },

    // --------------------
    // ACTIONS
    // --------------------
    async login() {
        return this._wrap(async () => {
            await this.$api.auth
                .login(this.username, this.password, this.rememberMe)
                .execute();

            this._redirect('/');
        });
    },

    async register() {
        return this._wrap(async () => {
            await this.$api.auth
                .register(
                    this.username,
                    this.password,
                    this.confirmPassword,
                    this.displayName
                )
                .execute();

            this._redirect('/auth/login');
        });
    },

    async setup() {
        return this._wrap(async () => {
            await this.$api.auth
                .setupAdmin(
                    this.username,
                    this.password,
                    this.confirmPassword
                )
                .execute();

            this._redirect('/auth/login');
        });
    },

    async logout() {
        await this.$api.auth.logout().execute();
        window.location.href = '/auth/login';
    },

    // --------------------
    // INTERNAL HELPERS
    // --------------------
    async _wrap(fn) {
        this.error = null;
        this.loading = true;
        this.success = false;

        try {
            await fn();
            this.success = true;
        } catch (err) {
            this.error =
                err?.detail?.detail ||
                err?.message ||
                'Something went wrong';
        } finally {
            this.loading = false;
        }
    },

    _redirect(url) {
        setTimeout(() => {
            window.location.href = url;
        }, 700);
    }
});
