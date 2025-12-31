export default () =>  ({
        isLoading: false,
        isSaving: false,
        
        collection: {
            ai_endpoint: '',
            base_llm: '',
            ai_key: '',
            temperature: 0.7,
            system_note: ''
        },

        async init() {
            await this.refresh();
        },

        async refresh() {
            this.isLoading = true;
            try {
                // Fetch current config
                const res = await this.$api.config.get().execute();
                
                // Map to collection
                this.collection.ai_endpoint = res.ai_endpoint || '';
                this.collection.base_llm = res.base_llm || '';
                this.collection.temperature = res.temperature !== undefined ? res.temperature : 0.7;
                this.collection.system_note = res.system_note || '';
                
                // Never populate the key field for security, it stays blank implies "no change"
                this.collection.ai_key = ''; 
            } catch (e) {
                console.error("Config Load Error", e);
            } finally {
                this.isLoading = false;
            }
        },

        async save() {
            this.isSaving = true;
            
            // Clone collection to avoid mutating UI state during save
            const payload = { ...this.collection };

            // If key is empty, don't send it (backend should treat this as "keep existing")
            if (!payload.ai_key || payload.ai_key.trim() === '') {
                delete payload.ai_key;
            }

            try {
                await this.$api.config.update().execute(payload);
                
                // Visual Feedback
                const btn = document.getElementById('save-config-btn');
                const oldHTML = btn.innerHTML;
                btn.innerHTML = `<i class="fas fa-check mr-2"></i> Saved!`;
                btn.classList.remove('bg-slate-900', 'hover:bg-slate-800');
                btn.classList.add('bg-green-600', 'hover:bg-green-700');
                
                setTimeout(() => {
                    btn.innerHTML = oldHTML;
                    btn.classList.add('bg-slate-900', 'hover:bg-slate-800');
                    btn.classList.remove('bg-green-600', 'hover:bg-green-700');
                }, 2000);

                // Reload to confirm values
                Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
                await this.refresh();

            } catch (e) {
                Alpine.store('notifications').error('Failed to Save Configuration', e); 
            } finally {
                this.isSaving = false;
                Alpine.store('notifications').success('Saved', 'Your changes have been applied.');
            }
        }
    });
