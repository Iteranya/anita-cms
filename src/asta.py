# file: services/markdown.py

import re
from typing import AsyncGenerator

from sqlalchemy.orm import Session
from src.llm import AIService
from data.schemas import Prompt as AIPrompt, MarkdownEditRequest

class MarkdownService:
    def __init__(self, db: Session):
        self.db = db
        # The MarkdownService depends on the AIService to function
        self.ai_service = AIService(db)

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

    async def generate_markdown(self, context: str, instruction: str) -> str:
        """
        Generates a new Markdown document from a context and an instruction.
        """
        system_note = f"<context>{context}</context>\nWrite only in Markdown Format."
        
        prompt = AIPrompt(
            system=system_note,
            user=instruction
        )
        
        result = await self.ai_service.generate_response(prompt)
        return result

    async def edit_markdown(self, task: MarkdownEditRequest) -> str:
        """
        Edits a selection of Markdown text based on multiple instructions.
        """
        system_note = (
            "Write only in Markdown Format.\n\n"
            "Follow the instruction provided. You must edit the selected text as instructed. "
            "Write the final, edited text ONLY inside <edited_content> </edited_content> tags. "
            "For example: <edited_content>\n# The Rewritten Passage\n\nIn Markdown Format.\n</edited_content>"
        )
        
        prompt_content = (
            f"<global_instruction>\n{task.global_instruction}\n</global_instruction>\n\n"
            f"<editor_content>\n{task.editor_content}\n</editor_content>\n\n"
            f"<selected_text>\n{task.selected_text}\n</selected_text>\n\n"
            f"<edit_instruction>\n{task.edit_instruction}</edit_instruction>"
        )

        prompt = AIPrompt(
            system=system_note,
            user=prompt_content
        )
        
        raw_result = await self.ai_service.generate_response(prompt)
        # Parse the result to extract only the edited content
        edited_result = self._regex_result(raw_result)
        return edited_result

    async def stream_markdown(self, context: str, instruction: str) -> AsyncGenerator[str, None]:
        """
        Streams a new Markdown document from a context and an instruction.
        """
        system_note = f"<context>{context}</context>\nWrite only in Markdown Format."
        
        prompt = AIPrompt(
            system=system_note,
            user=instruction
        )

        # The AIService's stream_response method is an async generator,
        # so we can directly yield from it.
        async for chunk in self.ai_service.stream_response(prompt):
            yield chunk