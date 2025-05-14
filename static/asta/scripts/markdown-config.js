// markdown-config.js
// Configure marked library for markdown parsing

export function configureMarked() {
    marked.setOptions({
        renderer: new marked.Renderer(),
        highlight: function(code, lang) {
            const language = hljs.getLanguage(lang) ? lang : 'plaintext';
            return `<pre><code class="language-${language}">${hljs.highlight(code, { language, ignoreIllegals: true }).value}</code></pre>`;
        },
        pedantic: false,
        gfm: true, // Enable GitHub Flavored Markdown
        breaks: true, // Enable GFM line breaks (\n becomes <br>)
        sanitize: false, // IMPORTANT: Set to true if dealing with untrusted input
        smartLists: true,
        smartypants: false,
        xhtml: false
    });
}

export const initialMarkdown = `# Welcome to the AI-Powered Markdown Editor! ✨

This editor allows you to write Markdown and see a live preview. You can also use the AI feature below to generate or modify content.

## Features

*   **Live Preview:** See your rendered Markdown instantly.
*   **Syntax Highlighting:** Code blocks are automatically highlighted.
*   **GitHub Flavored Markdown (GFM):** Supports tables, task lists, etc.
*   **AI Generation:** Describe changes and let the AI write Markdown for you!

---

## Examples

### Code Block (JavaScript)

\`\`\`javascript
// Simple fetch example
async function fetchData(url) {
try {
const response = await fetch(url);
if (!response.ok) {
throw new Error(\`HTTP error! status: \${response.status}\`);
}
const data = await response.json();
console.log('Data received:', data);
return data;
} catch (error) {
console.error('Could not fetch data:', error);
}
}

fetchData('https://jsonplaceholder.typicode.com/todos/1');
\`\`\`

### Blockquote

> "I alone am the exception..."
> *– Artes*

### Table

| Feature         | Status      | Priority | Notes                   |
|-----------------|-------------|----------|-------------------------|
| Live Preview    | ✅ Complete | High     | Core functionality      |
| Syntax Highlight| ✅ Complete | High     | Using highlight.js      |
| AI Integration  | ✅ Complete | Medium   | Connected to backend    |
| Sync Scrolling  | ✅ Complete | Low      | Enhances usability      |
| Theme Options   | ⏳ Planned  | Low      | Future enhancement      |

### Task List

- [x] Setup basic HTML structure
- [x] Implement Markdown parsing with Marked.js
- [x] Add syntax highlighting with Highlight.js
- [ ] Integrate AI generation form
- [ ] Implement AI streaming response handling

---

**Try editing this content or use the AI prompt below!**
`;