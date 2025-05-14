from src import llm
from data.models import Prompt
from concurrent.futures import ThreadPoolExecutor

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


async def stream_website(context, instruction):
    system_note = f"ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. Also, try to ellaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE \n\n <context> {context} </context>"
    prompt = f"{instruction}"

    new_prompt = Prompt(
        system=system_note,
        user=prompt,
        assistant="Understood, here's the requested site: ```html\n"
    )

    async for chunk in llm.stream_response(new_prompt):
        yield chunk  # Yield raw text chunk