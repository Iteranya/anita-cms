export default (slug) => {
    // 1. Define configuration
    const cspFields = [
        { id: 'default-src', category: 'Essentials', label: 'Default Fallback', description: 'The safety net. If a specific directive is missing, the browser uses this.', placeholder: "'none'" },
        { id: 'script-src', category: 'Essentials', label: 'Scripts', description: 'Whitelists allowed JavaScript sources. Critical for preventing XSS.', placeholder: "https://cdn.jsdelivr.net" },
        { id: 'style-src', category: 'Essentials', label: 'Styles', description: 'Whitelists allowed CSS stylesheets.', placeholder: "https://fonts.googleapis.com" },
        { id: 'connect-src', category: 'Fetch & Resources', label: 'Connections', description: 'Restricts URLs loaded by Fetch, XHR, and WebSockets.', placeholder: "https://api.stripe.com" },
        { id: 'img-src', category: 'Fetch & Resources', label: 'Images', description: 'Defines valid sources for images and favicons.', placeholder: "https://images.unsplash.com" },
        { id: 'font-src', category: 'Fetch & Resources', label: 'Fonts', description: 'Defines valid sources for web fonts.', placeholder: "https://fonts.gstatic.com" },
        { id: 'media-src', category: 'Fetch & Resources', label: 'Media', description: 'Defines valid sources for audio and video.', placeholder: "https://cdn.vid.com" },
        { id: 'object-src', category: 'Fetch & Resources', label: 'Plugins', description: 'Controls Flash/Java. Best set to \'none\'.', placeholder: "'none'" },
        { id: 'frame-src', category: 'Embeds & Workers', label: 'Iframe Sources', description: 'Whitelists domains YOU can embed as iframes.', placeholder: "https://www.youtube.com" },
        { id: 'worker-src', category: 'Embeds & Workers', label: 'Workers', description: 'Restricts Service Workers and Web Workers.', placeholder: "'self' blob:" },
        { id: 'manifest-src', category: 'Embeds & Workers', label: 'Manifest', description: 'Restricts where the Web App Manifest can load from.', placeholder: "'self'" },
        { id: 'base-uri', category: 'Security Boundaries', label: 'Base URI', description: 'Restricts the <base> element to prevent hijacking.', placeholder: "'self'" },
        { id: 'form-action', category: 'Security Boundaries', label: 'Form Actions', description: 'Restricts where forms can be submitted.', placeholder: "'self'" },
        { id: 'frame-ancestors', category: 'Security Boundaries', label: 'Frame Ancestors', description: 'Defines who can embed YOUR page.', placeholder: "'self' https://partner.com" },
    ];

    // 2. Pre-fill State
    const initialRules = {};
    const initialActive = {};
    
    cspFields.forEach(f => {
        initialRules[f.id] = [];
        initialActive[f.id] = false; // Default everything to OFF
    });

    return {
        slug: slug,
        isLoading: false,
        isSaving: false,
        saveStatus: 'Ready',
        
        // State
        customHeadContent: '', 
        cspState: {
            enabled: false,
            upgradeInsecure: false,
            rules: initialRules,
            active: initialActive // New: Track which specific rules are enabled
        },
        previewString: '',
        cspFields: cspFields,

        async init() {
            await this.loadHead();
        },

        async loadHead() {
            this.isLoading = true;
            try {
                const response = await this.$api.aina.get(this.slug).execute();
                const rawHtml = response.custom?.builder?.header || ''; 
                this.parseStateFromHtml(rawHtml);
                this.generatePreview(); 
            } catch (error) {
                console.error("Head load error", error);
            } finally {
                this.isLoading = false;
            }
        },

        parseStateFromHtml(html) {
            // Reset to clean slate
            this.cspState.enabled = false;
            this.cspState.upgradeInsecure = false;
            Object.keys(this.cspState.rules).forEach(k => {
                this.cspState.rules[k] = [];
                this.cspState.active[k] = false;
            });

            if (!html) {
                this.customHeadContent = '';
                return;
            }

            const cspRegex = /<meta http-equiv="Content-Security-Policy" content="([^"]+)">/i;
            const match = html.match(cspRegex);
            
            if (match) {
                this.cspState.enabled = true;
                const rawCspString = match[1];
                const directives = rawCspString.split(';').map(d => d.trim()).filter(d => d);

                directives.forEach(dir => {
                    if (dir === 'upgrade-insecure-requests') {
                        this.cspState.upgradeInsecure = true;
                        return;
                    }

                    const parts = dir.split(/\s+/);
                    const type = parts[0]; 
                    const values = parts.slice(1);

                    // If this directive exists in our known fields
                    if (this.cspState.rules[type] !== undefined) {
                        this.cspState.active[type] = true; // MARK AS ACTIVE

                        const ignored = ["'self'", "'unsafe-inline'", "'unsafe-eval'", "data:", "https:"];
                        const userValues = values.filter(v => !ignored.includes(v));
                        this.cspState.rules[type] = userValues;
                    }
                });

                this.customHeadContent = html.replace(match[0], '').trim();
            } else {
                this.customHeadContent = html;
            }
        },

        toggleCSP() {
            this.cspState.enabled = !this.cspState.enabled;
            
            // Optional: If enabling for the first time and everything is off, 
            // maybe enable 'default-src' so it does something. 
            // Or just leave it all blank as requested.
            if(this.cspState.enabled) {
                const isAllOff = Object.values(this.cspState.active).every(v => v === false);
                if(isAllOff) {
                    this.cspState.active['default-src'] = true;
                }
            }
            
            this.generatePreview();
        },

        addCspDomain(type, domain) {
            if (!domain) return;
            const d = domain.trim();
            if (!this.cspState.rules[type].includes(d)) {
                this.cspState.rules[type].push(d);
                this.generatePreview();
            }
        },

        removeCspDomain(type, index) {
            this.cspState.rules[type].splice(index, 1);
            this.generatePreview();
        },

        generatePreview() {
            const parts = [];
            if (this.customHeadContent && this.customHeadContent.trim() !== '') {
                parts.push(this.customHeadContent.trim());
            }
            if (this.cspState.enabled) {
                const cspString = this.buildCspMetaLabel();
                if(cspString) parts.push(cspString);
            }
            this.previewString = parts.join('\n\n');
        },

        buildCspMetaLabel() {
            let policies = [];

            if (this.cspState.upgradeInsecure) {
                policies.push('upgrade-insecure-requests');
            }

            // Helper to build a single directive string
            const build = (type, defaults = []) => {
                // KEY CHANGE: Check if this specific directive is active
                if (!this.cspState.active[type]) return null;

                const user = this.cspState.rules[type] || [];
                const merged = [...defaults, ...user];
                const unique = [...new Set(merged)];
                
                return `${type} ${unique.join(' ')}`;
            };

            // Define defaults here so we can inject them if active
            const defs = {
                'default-src': ["'self'"],
                'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
                'style-src': ["'self'", "'unsafe-inline'"],
                'img-src': ["'self'", "data:", "https:"],
                'connect-src': ["'self'"],
                'font-src': ["'self'"],
                'frame-ancestors': ["'self'"]
            };

            // Loop through all fields and build string if active
            this.cspFields.forEach(field => {
                const type = field.id;
                const defaults = defs[type] || ["'self'"];
                
                const directiveString = build(type, defaults);
                if (directiveString) {
                    policies.push(directiveString);
                }
            });

            if (policies.length === 0) return null;

            return `<meta http-equiv="Content-Security-Policy" content="${policies.join('; ')}">`;
        },

        async saveHead() {
            this.isSaving = true;
            this.saveStatus = 'Saving...';
            
            this.generatePreview(); 

            try {
                const currentData = await this.$api.aina.get(this.slug).execute();
                const existingBuilder = currentData.custom?.builder || {};

                const newBuilder = { ...existingBuilder, header: this.previewString };
                delete newBuilder.headConfig; 

                const payload = {
                    custom: {
                        builder: newBuilder
                    }
                };

                await this.$api.aina.updateHTML().execute(this.slug, payload);

                this.saveStatus = 'Saved';
                setTimeout(() => { this.saveStatus = 'Ready'; }, 2000);
            } catch (error) {
                console.error("Head save error", error);
                this.saveStatus = 'Error';
            } finally {
                this.isSaving = false;
            }
        }
    };
};