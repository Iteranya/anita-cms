import config
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import asyncio
from openai import OpenAI
from src import config
import re
from data.models import Prompt
from src import llm

def title_to_filename(title):
    # Convert to lowercase
    filename = title.lower()
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '-')
    
    # Remove special characters
    import re
    filename = re.sub(r'[^\w\s_-]', '', filename)
    
    return filename

async def generate_markdown(context,instruction):
    system_note = f"<context>{context}</context>\nWrite only in Markdown Format."
    prompt = f"{instruction}"

    new_prompt = Prompt(
        system= f"{system_note}",
        user= prompt,
        assistant="Understood, here's the rewritten content"
    )
    
    result = await llm.generate_response(new_prompt)
    return str(result)

async def edit_with_llm(task):
    system_note = "Write only in Markdown Format"
    global_instruction = str(task["global_instruction"]) # The Pane
    edit_instruction = str(task["edit_instruction"]) # From Modal
    editor_content = str(task["editor_content"]) # From Editor
    selected_text = str(task["selected_text"]) # Selected Text
    prompt = "<global_instruction>\n"+ global_instruction + "\n</global_instruction>\n\n<editor_content>"+editor_content + "\n</editor_content>\n\n<selected_text>\n"+selected_text+"\n</selected_text>\n\n<edit_instruction>"+edit_instruction+"</edit_instruction>"

    # print(f"Generating Doc~\n\n Prompt: {edit}")
    
    new_prompt = Prompt(
        system= f"{system_note}\n\nFollow the instruction provided. You must edit the selected text as instruucted. Write it between <edited_content> </edited_content> tags. For example: <edited_content>\n# The Rewritten Passage \n\n In Markdown Format.\n</edited_content>",
        user= prompt,
        assistant="Understood, here's the rewritten content"

    )
    
    result = await llm.generate_response(new_prompt)
    result = regex_result(result)
    return str(result)


def regex_result(content: str):
    match = re.search(r'<edited_content>(.*?)</edited_content>', content, re.DOTALL)
    if match:
        return match.group(1)
    return None