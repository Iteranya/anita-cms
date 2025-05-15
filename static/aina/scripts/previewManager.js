import { getProject } from "./dbIntegration.js";

export async function initPreview(htmlCode, preview, slug) {
    // Set up event listener for editor changes
    htmlCode.addEventListener('input', () => updatePreview(htmlCode, preview));
    // Initial update
    const project = await getProject(slug);  // Added 'const' declaration here
    if (project.html) {
        htmlCode.value = project.html;
    }
    

    updatePreview(htmlCode, preview);
}

export function updatePreview(htmlCode, preview) {
    const previewDoc = preview.contentDocument || preview.contentWindow.document;
    previewDoc.open();
    previewDoc.write(htmlCode.value);
    previewDoc.close();
}