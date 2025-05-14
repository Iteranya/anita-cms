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
        
        // Prepare data for the backend
        const currentMarkdown = String(this.editor.getValue());
        const side_panel = String(this.side_panel.value);
        const context = "<notes>\n"+ side_panel + "\n</notes>\n\n<markdown_content>"+currentMarkdown + "\n</markdown_content>\n"
        const requestData = {
            current_markdown: context,
            prompt: promptValue
        };
        
        try {
            // STEP 1: Send request to initiate generation
            const response = await fetch('/generate-doc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                let errorMsg = 'Failed to initiate AI generation.';
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || errorMsg;
                } catch (jsonError) {
                    // Ignore if response is not JSON
                }
                throw new Error(errorMsg);
            }
            
            const data = await response.json();
            
            if (data.id) {
                await this.handleStreamResponse(data.id);
            } else {
                throw new Error("Failed to get stream ID from server.");
            }
            
        } catch (error) {
            console.error('Error during AI generation:', error);
            this.resetFormState();
            NotificationSystem.show(`Yabai! ${error.message || 'Something went wrong'} (╥﹏╥)`, 'error');
        }
    }
    
    async handleStreamResponse(streamId) {
        // Append a clear indicator before starting the stream        
        const eventSource = new EventSource(`/stream/${streamId}`);
        let generatedMarkdown = '';
        let isFirstChunk = true;
        
        eventSource.onmessage = (event) => {
            try {
                const eventData = JSON.parse(event.data);
                
                if (eventData.markdown_chunk) {
                    generatedMarkdown += eventData.markdown_chunk;
                    // Append chunk to the textarea
                    this.editor.appendValue(eventData.markdown_chunk);
                    
                    // Scroll to the bottom of the textarea
                    this.editor.scrollToBottom();
                    isFirstChunk = false;
                }
                
                if (eventData.done) {
                    eventSource.close();
                    this.resetFormState();
                    this.promptTextarea.value = ''; // Clear prompt on success
                    
                    // Show completion notification
                    NotificationSystem.show('✧･ﾟ:* AI Generation Complete! *:･ﾟ✧', 'success');
                }
            } catch (parseError) {
                console.error("Error parsing stream data:", parseError, "Raw data:", event.data);
            }
        };
        
        eventSource.onerror = (error) => {
            console.error("EventSource failed:", error);
            eventSource.close();
            this.resetFormState();
            NotificationSystem.show('Stream connection error (╥﹏╥)', 'error');
        };
    }
    
    resetFormState() {
        this.submitButton.disabled = false;
        this.submitButton.innerHTML = this.originalButtonText;
    }
}