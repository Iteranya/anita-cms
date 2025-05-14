export async function generateLatex(project) {
    console.log(project)
    const markdown_content = project.markdown;
    const template = project.type || "default.tex"; // fallback to default if not provided
    const output = project.slug+"/content.tex";

    try {
        const response = await fetch('/generate-latex/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                markdown: markdown_content,
                output_path: output,
                template: template,
            }),
        });

        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();

        if (data && data.latex) {
            return data.latex; // Return the generated LaTeX content
        } else {
            throw new Error("No LaTeX content returned from server.");
        }
    } catch (error) {
        console.error("Failed to generate LaTeX:", error);
        throw error;
    }
}