import { getProject } from "./dbIntegration.js";

export async function initPreview(htmlCode, preview, slug) {

    // 1. Iframe Sandbox (Layer 1 Security)
    // allow-scripts: Required for Alpine
    // allow-modals: Optional (for alerts)
    // We do NOT add 'allow-forms' or 'allow-same-origin'
    preview.setAttribute('sandbox', 'allow-scripts allow-modals');

    // Set up event listener for editor changes
    htmlCode.addEventListener('input', () => updatePreview(htmlCode, preview));
    
    // Initial update
    if(slug){
        const project = await getProject(slug);
        if (project.html) {
            htmlCode.value = project.html;
        }
    }
   
    updatePreview(htmlCode, preview);
}

export function updatePreview(htmlCode, preview) {
    const previewDoc = preview.contentDocument || preview.contentWindow.document;

    // 2. CSP Definition (Layer 2 Security)
    // connect-src 'none': This is the key. It completely disables fetch/xhr.
    const cspContent = `
        default-src 'none';
        script-src 'unsafe-inline' 'unsafe-eval' https:;
        style-src 'unsafe-inline' https:;
        img-src 'self' data: https:;
        font-src 'self' data: https:;
        connect-src 'none';
        form-action 'none';
    `;
    
    const cspMeta = `<meta http-equiv="Content-Security-Policy" content="${cspContent}">`;

    let content = htmlCode.value;

    // 3. Smart Injection
    // We want the CSP to be the very first thing in the <head> to ensure it loads
    // before any other scripts run.
    
    if (/<head/i.test(content)) {
        // If <head> exists, inject immediately after the opening <head> tag
        content = content.replace(/<head[^>]*>/i, (match) => match + cspMeta);
    } 
    else if (/<html/i.test(content)) {
        // If no <head> but <html> exists, inject after <html> 
        // (Browser will implicitly create a head for the meta tag)
        content = content.replace(/<html[^>]*>/i, (match) => match + cspMeta);
    } 
    else {
        // Fallback: If the user just wrote raw <div>... without html/head tags
        content = cspMeta + content;
    }

    previewDoc.open();
    previewDoc.write(content);
    previewDoc.close();
}