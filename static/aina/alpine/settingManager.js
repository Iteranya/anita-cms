export default (slug) => ({
    slug: slug,
    isLoading: false,
    isSaving: false,
    saveStatus: 'Ready',
    
    // --- State (Rebuilt from HTML every load) ---
    // We use a Set for O(1) lookups, similar to selectedSlugs in generatorManager
    activeModules: new Set(), 
    
    cspState: {
        enabled: false,
        rules: {
            'script-src': [],
            'style-src': [],
            'connect-src': [],
            'img-src': [],
            'frame-ancestors': [] 
        }
    },

    // Current Raw HTML (for previewing)
    previewString: '',

    // --- Configuration / Dictionary ---
    // identifyingPart: A unique string/regex used to detect if this module is already inside the HTML
    definitions: [
        {
            category: "Essentials",
            items: [
                { 
                    id: 'charset', 
                    type: 'boolean', 
                    label: 'UTF-8 Charset', 
                    desc: 'Standard character encoding.', 
                    snippet: '<meta charset="UTF-8">',
                    identifyingPart: 'charset="UTF-8"' 
                },
                { 
                    id: 'viewport', 
                    type: 'boolean', 
                    label: 'Responsive Viewport', 
                    desc: 'Essential for mobile responsiveness.', 
                    snippet: '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                    identifyingPart: 'name="viewport"' 
                },
                {
                    id: 'jquery',
                    type: 'boolean',
                    label: 'jQuery 3.7.0',
                    desc: 'Legacy DOM manipulation.',
                    snippet: '<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>',
                    identifyingPart: 'code.jquery.com/jquery-3.7.0'
                }
            ]
        },
        {
            category: "UI Frameworks",
            items: [
                { 
                    id: 'tailwind', 
                    type: 'boolean', 
                    label: 'Tailwind CSS (CDN)', 
                    desc: 'Utility-first CSS framework.', 
                    snippet: '<script src="/static/hikarin/lib/tailwind.js"></script>',
                    identifyingPart: 'cdn.tailwindcss.com' 
                },
                { 
                    id: 'alpine', 
                    type: 'boolean', 
                    label: 'Alpine.js', 
                    desc: 'Lightweight JavaScript framework.', 
                    snippet: '<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"></script>',
                    identifyingPart: 'alpinejs@3.13.3' 
                },
                { 
                    id: 'fontawesome', 
                    type: 'boolean', 
                    label: 'FontAwesome 6', 
                    desc: 'Icon library.', 
                    snippet: '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
                    identifyingPart: 'font-awesome/6.4.0' 
                }
            ]
        },
        {
            category: "Security",
            isSecurity: true,
            items: [
                { id: 'csp_master', type: 'master_switch', label: 'Enable CSP', desc: 'Content Security Policy' },
                { id: 'script-src', type: 'list', label: 'Scripts (script-src)', placeholder: 'https://api.google.com' },
                { id: 'style-src', type: 'list', label: 'Styles (style-src)', placeholder: 'https://fonts.googleapis.com' },
                { id: 'connect-src', type: 'list', label: 'Connections (connect-src)', placeholder: 'https://api.stripe.com' }
            ]
        }
    ],

    // --- Lifecycle ---

    async init() {
        await this.loadHead();
    },

    // --- Parsing Logic (The Generator Technique) ---

    async loadHead() {
        this.isLoading = true;
        try {
            const response = await this.$api.aina.get(this.slug).execute();
            // This raw string is our ONLY source of truth
            const rawHtml = response.custom?.builder?.header || ''; 
            
            this.parseStateFromHtml(rawHtml);
            this.generatePreview(); // Sync preview string

        } catch (error) {
            console.error("Head load error", error);
        } finally {
            this.isLoading = false;
        }
    },

    parseStateFromHtml(html) {
        // 1. Reset State
        this.activeModules.clear();
        this.cspState.enabled = false;
        Object.keys(this.cspState.rules).forEach(k => this.cspState.rules[k] = []);

        if (!html) return;

        // 2. Detect Modules (Booleans)
        this.definitions.forEach(group => {
            group.items.forEach(item => {
                if (item.type === 'boolean' && item.identifyingPart) {
                    if (html.includes(item.identifyingPart)) {
                        this.activeModules.add(item.id);
                    }
                }
            });
        });
        
        // 3. Detect CSP (The complex part)
        // Regex to extract the content="..." from the meta label
        const cspMatch = html.match(/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/);
        
        if (cspMatch) {
            this.cspState.enabled = true;
            const rawCspString = cspMatch[1];
            
            // Split directives (e.g., "script-src 'self'; style-src 'self'")
            const directives = rawCspString.split(';').map(d => d.trim()).filter(d => d);

            directives.forEach(dir => {
                const parts = dir.split(/\s+/);
                const type = parts[0]; // e.g., 'script-src'
                const values = parts.slice(1); // e.g., ["'self'", "https://cdn.foo.com"]

                if (this.cspState.rules[type]) {
                    // Filter out standard keywords we add automatically, so we only show USER CUSTOM domains
                    const ignored = ["'self'", "'unsafe-inline'", "'unsafe-eval'", "data:", "https:"];
                    
                    // Also filter out domains belonging to active modules (e.g. if Tailwind is on, don't show cdn.tailwindcss.com in the list)
                    const moduleDomains = this.getImpliedDomains(type);
                    
                    const userValues = values.filter(v => 
                        !ignored.includes(v) && 
                        !moduleDomains.includes(v)
                    );

                    this.cspState.rules[type] = userValues;
                }
            });
        }
        
        // Force reactivity for the Set
        this.activeModules = new Set(this.activeModules); 
    },

    // --- UI Actions ---

    toggleModule(id) {
        if (this.activeModules.has(id)) {
            this.activeModules.delete(id);
        } else {
            this.activeModules.add(id);
        }
        this.activeModules = new Set(this.activeModules);
        this.generatePreview();
    },

    isModuleActive(id) {
        return this.activeModules.has(id);
    },

    toggleCSP() {
        this.cspState.enabled = !this.cspState.enabled;
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

    // --- Compiler (State -> HTML String) ---

    generatePreview() {
        let lines = [];
        
        // 1. Add Enabled Modules
        this.definitions.forEach(group => {
            group.items.forEach(item => {
                if (item.type === 'boolean' && this.activeModules.has(item.id)) {
                    lines.push(item.snippet);
                }
            });
        });

        // 2. Add CSP if enabled
        if (this.cspState.enabled) {
            lines.push(this.buildCspMetaLabel());
        }

        this.previewString = lines.join('\n');
    },

    buildCspMetaLabel() {
        let policies = [];
        
        // Base Policy
        policies.push("default-src 'self'");
        policies.push("img-src 'self' data: https:");

        // Helper to get domains that are implied by currently active modules
        // e.g. if 'tailwind' is active, we need 'https://cdn.tailwindcss.com'
        const getMergedList = (type) => {
            const defaults = ["'self'", "'unsafe-inline'", "'unsafe-eval'"];
            const implied = this.getImpliedDomains(type);
            const user = this.cspState.rules[type] || [];
            return [...defaults, ...implied, ...user];
        };

        policies.push(`script-src ${getMergedList('script-src').join(' ')}`);
        policies.push(`style-src ${getMergedList('style-src').join(' ')}`);
        
        // Connect Src (usually just user defined + self)
        const connectList = ["'self'", ...this.cspState.rules['connect-src']];
        if (connectList.length > 1) {
            policies.push(`connect-src ${connectList.join(' ')}`);
        }

        return `<meta http-equiv="Content-Security-Policy" content="${policies.join('; ')}">`;
    },

    // Lookup table for domains required by modules
    getImpliedDomains(type) {
        const domains = [];
        
        if (type === 'script-src') {
            if (this.activeModules.has('tailwind')) domains.push('https://cdn.tailwindcss.com');
            if (this.activeModules.has('alpine')) domains.push('https://cdn.jsdelivr.net');
            if (this.activeModules.has('jquery')) domains.push('https://code.jquery.com');
        }
        
        if (type === 'style-src') {
            if (this.activeModules.has('fontawesome')) domains.push('https://cdnjs.cloudflare.com');
        }

        return domains;
    },

    // --- Saving ---

    async saveHead() {
        this.isSaving = true;
        this.saveStatus = 'Saving...';
        
        // Ensure string is fresh
        this.generatePreview();

        try {
            const currentData = await this.$api.aina.get(this.slug).execute();
            const existingBuilder = currentData.custom?.builder || {};

            // CLEANUP: We are removing headConfig if it existed previously
            // We only save 'header' (the raw string)
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
});