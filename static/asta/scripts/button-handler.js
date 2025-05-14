import { NotificationSystem } from './notification-system.js';
import { updateProject, getProject } from './db-integration.js';
import { generateLatex } from './latex-integration.js';

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

    static async handleLatexButton(slug, markdown, aiNotes) {
        console.log("Inside latex handler: "+slug)
        try {
            const project = await getProject(slug);
            
            if (!project.markdown) {
                throw new Error("Project has no markdown content to convert");
            }
    
            // Generate LaTeX content
            console.log("Inside Handle Latex: "+ project.slug)
            const latexContent = await generateLatex(project);
            
            // Create a Blob with the LaTeX content
            const blob = new Blob([latexContent], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            
            // Create a temporary anchor element to trigger download
            const a = document.createElement('a');
            a.href = url;
            a.download = `${project.slug || 'document'}.tex`;  // Use slug as filename or fallback
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            NotificationSystem.show('LaTeX document downloaded successfully!', 'success');
            return { success: true };
        } catch (error) {
            console.error("Error generating LaTeX:", error);
            NotificationSystem.show(`Failed to generate LaTeX: ${error.message}`, 'error');
            return { success: false, error };
        }
    }

    static async handleProjectButton(slug, markdown, aiNotes) {
        console.log("Inside project handler: "+slug)
        try {
    
            // First update the project to ensure we have the latest content
            const project_data = await getProject(slug);
            project_data.ai_notes = aiNotes;
            project_data.markdown = markdown;
            await updateProject(slug, project_data);
    
            // Generate the download URL
            const downloadUrl = `/generate_project_zip/${slug}`;
            
            // Create a temporary anchor element to trigger download
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `${slug}.zip`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            document.body.removeChild(a);
            
            NotificationSystem.show('Project ZIP downloaded successfully!', 'success');
            return { success: true };
        } catch (error) {
            console.error("Error downloading project ZIP:", error);
            NotificationSystem.show(`Failed to download project ZIP: ${error.message}`, 'error');
            return { success: false, error };
        }
    }
}