import { getProject,updateProject } from "./dbIntegration.js";
import { showNotification } from "./notifications.js";


export async function setupDeployment(htmlCode,slug) {
    // Open deployment modal
    document.getElementById('deploy-btn').addEventListener('click', async () => {
        try {
            const project_data = await getProject(slug);
            project_data.html = htmlCode.value;
           
            const result = await updateProject(slug, project_data);
            console.log(result);
           showNotification("Project Updated Successfully","success")
            return { success: true };
        } catch (error) {
            console.error("Error updating project:", error);
            showNotification(`Failed to update project: ${error.message}`,"error");
            return { success: false, error };
        }
    });
}