import config
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import asyncio
from openai import OpenAI
from src import config
import re


# Create a thread pool for CPU-bound tasks
executor = ThreadPoolExecutor()

def title_to_filename(title):
    # Convert to lowercase
    filename = title.lower()
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '-')
    
    # Remove special characters
    import re
    filename = re.sub(r'[^\w\s_-]', '', filename)
    
    return filename

# Store active generation tasks
active_generations = {}

async def generate_html_stream(content, generation_id):
    ai_config:config.Config = config.load_or_create_config()

    client = OpenAI(
        base_url=ai_config.ai_endpoint,
        api_key=config.get_key(),
    )
    try:
        print(content)
        # Create the prompt
        messages = [
            {
            "role": "system",
            "content": ai_config.system_note
            },
            {
            "role": "user",
            "content": f"{content}"
            },
            {
            "role": "assistant",
            "content": "Understood, here's the markdown content: ```\n"
            }
        ]
        
        # Use synchronous client with stream=True for streaming
        stream = client.chat.completions.create(
            model=ai_config.base_llm,
            messages=messages,
            stream=True
        )
        
        html_so_far = ""
        # Iterate through the stream (this works synchronously)
        for chunk in stream:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                html_so_far += delta_content
                # Store this chunk
                if generation_id in active_generations:
                    active_generations[generation_id]["chunks"].append(delta_content)
                await asyncio.sleep(0.01)  # Small delay to prevent CPU overload
        
        return html_so_far
    except Exception as e:
        print(f"Error in generation: {str(e)}")
        return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"
    
async def edit_with_ai(task):

    ai_config:config.Config = config.load_or_create_config()

    client = OpenAI(
        base_url=ai_config.ai_endpoint,
        api_key= config.get_key(),
        )

    global_instruction = str(task["global_instruction"]) # The Pane
    edit_instruction = str(task["edit_instruction"]) # From Modal
    editor_content = str(task["editor_content"]) # From Editor
    selected_text = str(task["selected_text"]) # Selected Text

    prompt = "<global_instruction>\n"+ global_instruction + "\n</global_instruction>\n\n<editor_content>"+editor_content + "\n</editor_content>\n\n<selected_text>\n"+selected_text+"\n</selected_text>\n\n<edit_instruction>"+edit_instruction+"</edit_instruction>"

    # print(f"Generating Doc~\n\n Prompt: {edit}")
    
    completion = client.chat.completions.create(
    model=ai_config.base_llm,
    messages=[
        {
        "role": "system",
        "content": f"{ai_config.system_note}\n\nFollow the instruction provided. You must edit the selected text as instruucted. Write it between <edited_content> </edited_content> tags. For example: <edited_content>\n# The Rewritten Passage \n\n In Markdown Format.\n</edited_content>"
        },
        {
        "role": "user",
        "content": prompt
        },
        {
        "role": "assistant",
        "content": "Understood, here's the rewritten content"
        }
    ]
    )
    result = completion.choices[0].message.content
    result = regex_result(result)
    return str(result)


def regex_result(content: str):
    match = re.search(r'<edited_content>(.*?)</edited_content>', content, re.DOTALL)
    if match:
        return match.group(1)
    return None