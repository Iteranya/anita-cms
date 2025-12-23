# file: services/markdown.py

import re

from sqlalchemy.orm import Session

class MarkdownService:
    def __init__(self, db: Session):
        self.db = db
        # The MarkdownService depends on the AIService to function
    
    def _regex_result(self, content: str) -> str:
        """
        Extracts content from within <edited_content> tags.
        Returns the extracted content or an empty string if not found.
        """
        match = re.search(r'<edited_content>(.*?)</edited_content>', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Return the original content as a fallback if tags are missing
        return content 