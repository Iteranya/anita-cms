from openai import AsyncOpenAI  # Use AsyncOpenAI instead
from data.models import Prompt
from src.config import load_or_create_config, DefaultConfig, get_key

async def generate_response(task: Prompt):
    ai_config: DefaultConfig = load_or_create_config()
    client = AsyncOpenAI(  # Changed to AsyncOpenAI
        base_url=task.endpoint or ai_config.ai_endpoint,
        api_key=task.ai_key or get_key(),
    )
    
    completion = await client.chat.completions.create(  # Added await
        model=task.model or ai_config.base_llm,
        stop=task.stop or [],
        temperature=task.temp or ai_config.temperature,
        messages=[
            {"role": "system", "content": task.system},
            {"role": "user", "content": task.user},
            {"role": "assistant", "content": task.assistant}
        ]
    )
    result = completion.choices[0].message.content
    task.result = result
    return task.result

async def generate_chat(message:list):
    ai_config: DefaultConfig = load_or_create_config()
    client = AsyncOpenAI(  # Changed to AsyncOpenAI
        ai_config.ai_endpoint,
        get_key(),
    )
    
    completion = await client.chat.completions.create(  # Added await
        ai_config.base_llm,
        ai_config.temperature,
        messages=message
    )
    result = completion.choices[0].message.content
    return result

async def stream_response(task: Prompt):
    ai_config: DefaultConfig = load_or_create_config()
    client = AsyncOpenAI(  # Changed to AsyncOpenAI
        base_url=task.endpoint or ai_config.ai_endpoint,
        api_key=task.ai_key or get_key(),
    )
    
    stream = await client.chat.completions.create(  # Added await
        model=task.model or ai_config.base_llm,
        stop=task.stop or [],
        temperature=task.temp or ai_config.temperature,
        messages=[
            {"role": "system", "content": task.system},
            {"role": "user", "content": task.user}
        ],
        stream=True,
    )
    
    full_response = ""
    async for chunk in stream:  # Changed to async for
        if chunk.choices[0].delta and chunk.choices[0].delta.content:
            content_piece = chunk.choices[0].delta.content
            full_response += content_piece
            yield content_piece
    
    task.result = full_response


async def stream_message_response(task: Prompt,messages):
    ai_config: DefaultConfig = load_or_create_config()
    client = AsyncOpenAI(  # Changed to AsyncOpenAI
        base_url=ai_config.ai_endpoint,
        api_key= get_key(),
    )
    
    stream = await client.chat.completions.create(  # Added await
        model=task.model or ai_config.base_llm,
        stop=task.stop or [],
        temperature=task.temp or ai_config.temperature,
        messages = messages,
        stream=True,
    )
    
    full_response = ""
    async for chunk in stream:  # Changed to async for
        if chunk.choices[0].delta and chunk.choices[0].delta.content:
            content_piece = chunk.choices[0].delta.content
            full_response += content_piece
            yield content_piece
    
    task.result = full_response