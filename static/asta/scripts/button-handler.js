import { NotificationSystem } from './notification-system.js';
import { updateProject, getProject } from './db-integration.js';

export class ButtonHandlers {
    static async handleActionButton(slug, markdown, aiNotes) {
        console.log("Inside button-handler: "+slug)
        try {
            const project_data = await getProject(slug);
            project_data.ai_notes = aiNotes;
            project_data.markdown = markdown;
            
            const result = await updateProject(slug, project_data);
            console.log(result);
            NotificationSystem.show('Project updated successfully!', 'success');
            return { success: true };
        } catch (error) {
            console.error("Error updating project:", error);
            NotificationSystem.show(`Failed to update project: ${error.message}`, 'error');
            return { success: false, error };
        }
    }
}