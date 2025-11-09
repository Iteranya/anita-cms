import markdown as md_lib
from jinja2 import Template

def generate_markdown_page(title: str, md: str, template_content: str = None):
    
    if template_content == None:
        template_content = load_from_file("static/markdown/index.html")
    
    html_content = md_lib.markdown(
        md,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.codehilite',
            'markdown.extensions.nl2br'
        ]
    )
    
    template = Template(template_content)
    html = template.render(
        title=title,
        content=html_content
    )
    
    return html

def load_from_file(filename):
    with open(filename, 'r') as f:
        return f.read()