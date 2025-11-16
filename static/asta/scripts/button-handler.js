import { NotificationSystem } from './notification-system.js';
import { updateProject, getProject } from './db-integration.js';

export class ButtonHandlers {
    /**
     * Handles the action button click to update a project.
     * @param {string} slug - The project's unique identifier.
     * @param {string} markdown - The main markdown content.
     * @param {string} aiNotes - The notes from the sidebar.
     * @param {string[]} project_tags - The array of tags for the project.
     * @param {boolean} isBlog - True if the blog toggle is on.
     */
    static async handleActionButton(slug, markdown, aiNotes, project_tags, isBlog) {
        console.log(`Inside button-handler: ${slug}, isBlog: ${isBlog}`);
        try {
            // Get the most recent version of the project
            const project_data = await getProject(slug);

            // Update the fields from the UI
            project_data.ai_notes = aiNotes;
            project_data.markdown = markdown;
            project_data.tags = project_tags;

            // --- NEW LOGIC ---
            // If the toggle is on, set the project type to 'markdown'
            if (isBlog) {
                project_data.type = 'markdown';
            } 

            const result = await updateProject(slug, project_data);
            console.log("Project updated:", result);
            NotificationSystem.show('Project updated successfully!', 'success');
            return { success: true };
        } catch (error) {
            console.error("Error updating project:", error);
            NotificationSystem.show(`Failed to update project: ${error.message}`, 'error');
            return { success: false, error };
        }
    }
}