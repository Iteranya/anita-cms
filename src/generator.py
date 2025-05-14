import markdown as md_lib

def generate_markdown_page(title:str,md: str, css = "static/public/styles.css", js = "static/public/script.js"):

    custom_css = load_from_file(css)
    custom_js = load_from_file(js)
    # Convert markdown to HTML
    html_content = md_lib.markdown(
        md,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.codehilite',
            'markdown.extensions.nl2br'
        ]
    )
    
    # Create a basic HTML document structure with embedded CSS
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{custom_css}
</style>
</head>
<body>
<div class="markdown-content">
    {html_content}
</div>
<script>
{custom_js}
</script>
</body>
</html>"""
    
    return html

def load_from_file(filename):
    with open(filename, 'r') as f:
        return f.read()