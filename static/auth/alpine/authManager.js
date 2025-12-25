export default () => ({
    username: '',
    password: '',
    confirmPassword: '',
    displayName: '',
    rememberMe: false,

    loading: false,
    error: null,
    success: false,
    mode: 'login',

    async init() {
        // Only run setup check if we are on login/register pages
        // to prevent infinite loops if the check fails
        if (['login', 'register'].includes(this.mode)) {
            try {
                // We use a silent check (no global loader overlay)
                const res = await this.$api.auth.checkSetup().run();
                if (!res.initialized) {
                    console.warn("System not initialized. Redirecting to setup.");
                    window.location.href = '/auth/setup';
                }
            } catch (err) {
                console.error("Setup check failed", err);
            }
        }
    },

    async login() {
        this.error = null;
        this.loading = true;
        
        try {
            const res = await this.$api.auth
                .login(this.username, this.password, this.rememberMe)
                .execute();

            // Store notification if needed or just redirect
            this.success = true;
            
            // Artificial delay for UX (so they see the success state)
            setTimeout(() => {
                window.location.href = '/'; 
            }, 500);

        } catch (err) {
            this.error = err.detail?.detail || "Invalid credentials";
            this.password = ''; // clear password on fail
        } finally {
            this.loading = false;
        }
    },
    
    
    // --------------------
    // ACTIONS
    // --------------------

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