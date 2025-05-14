from openai import OpenAI
from data.models import Prompt
from src.config import load_or_create_config,DefaultConfig,get_key

async def generate_response(task:Prompt):
    ai_config:DefaultConfig = load_or_create_config()
    client = OpenAI(
        base_url=task.endpoint or ai_config.ai_endpoint,
        api_key= task.ai_key or get_key(),
        )
    
    completion = client.chat.completions.create(
    model=task.model or ai_config.base_llm,
    stop=task.stop or [],
    temperature=task.temp or ai_config.temperature, # I forgor :3
    messages=[
        {
        "role":"system",
        "content":task.system
        },
        {
        "role": "user",
        "content": task.user
        },
        {
        "role": "assistant",
        "content": task.assistant
        }
    ]
    )
    result = completion.choices[0].message.content
    task.result = result
    return task