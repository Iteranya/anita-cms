// ai-integration.js
// AI-powered content generation functionality

import { NotificationSystem } from './notification-system.js';

export class AiGenerator {
    constructor(editorInstance) {
        this.editor = editorInstance;
        this.side_panel =  document.getElementById('sidebar-textarea');
        this.form = document.getElementById('ai-form');
        this.promptTextarea = document.getElementById('ai-prompt');
        this.submitButton = this.form.querySelector('button');
        this.originalButtonText = this.submitButton.innerHTML;
        
        if (!this.form || !this.promptTextarea) {
            console.error("AI form or prompt textarea not found!");
            return;
        }
        
        // Set up event listeners
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const promptValue = this.promptTextarea.value.trim();
        
        if (!promptValue) {
            NotificationSystem.show('Please enter a prompt for the AI.', 'error');
            this.promptTextarea.focus();
            return;
        }
        
        // Show loading state
        this.submitButton.disabled = true;
        this.submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        
        const currentMarkdown = String(this.editor.getValue());
        const side_panel = String(this.side_panel.value);
        const context = "<notes>\n" + side_panel + "\n</notes>\n\n<markdown_content>" + currentMarkdown + "\n</markdown_content>\n";
        const requestData = {
            current_markdown: context,
            prompt: promptValue
        };

        try {
            const response = await fetch('/asta/generate-doc-stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok || !response.body) {
                throw new Error('Failed to connect to stream.');
            }

            await this.handleStreamResponse(response.body);

        } catch (error) {
            console.error('Error during AI generation:', error);
            this.resetFormState();
            NotificationSystem.show(`Yabai! ${error.message || 'Something went wrong'} (╥﹏╥)`, 'error');
        }
    }

    async handleStreamResponse(stream) {
        const reader = stream.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;
        let fullContent = '';

        while (!done) {
            const { value, done: streamDone } = await reader.read();
            if (value) {
                const chunk = decoder.decode(value, { stream: !streamDone });
                fullContent += chunk;
                this.editor.appendValue(chunk);
                this.editor.scrollToBottom();
            }
            done = streamDone;
        }

        this.resetFormState();
        this.promptTextarea.value = ''; // Clear prompt
        NotificationSystem.show('✧･ﾟ:* AI Generation Complete! *:･ﾟ✧', 'success');
    }

    resetFormState() {
        this.submitButton.disabled = false;
        this.submitButton.innerHTML = this.originalButtonText;
    }
}
