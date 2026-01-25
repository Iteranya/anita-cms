# file: services/aina.py

import re
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session


# --- Helper Classes and Functions ---
    
def title_to_filename(title: str) -> str:
    """Converts a string into a URL-friendly slug."""
    filename = title.lower()
    filename = filename.replace(' ', '-')
    filename = re.sub(r'[^\w\s_-]', '', filename)
    return filename

# --- Main Service Class ---

class WebsiteBuilderService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_page_style_description(self, html: str) -> str: # Not used in AlpineData, this is for something else
        """Parses HTML to extract styling and structural elements for AI context."""
        if not html: 
            return ""
        soup = BeautifulSoup(html, 'html.parser')
        components = []
        head = soup.find('head')
        if head:
            labels = head.find_all(['script', 'style', 'link'])
            for label in labels:
                if label.name == 'link' and label.get('rel') == ['stylesheet']:
                    components.append(str(label))
                elif label.name in ['script', 'style']:
                    components.append(str(label))
        navbar = soup.find('nav') or soup.find('header')
        if navbar: 
            components.append(str(navbar))
        footer = soup.find('footer')
        if footer: 
            components.append(str(footer))
        if components: 
            return f"{' '.join(components)}\n\nMake the site based on this style."
        return ""
