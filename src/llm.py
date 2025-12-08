

from typing import List, Dict, AsyncGenerator
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from openai import AsyncOpenAI

from services.config import ConfigService
from data.schemas import Prompt

class AIService:
    def __init__(self, db: Session):
        """
        Initializes the AI Service by loading necessary configuration from the database.
        """
        self.db = db
        config_service = ConfigService(self.db)

        # Load essential settings from the database
        self.base_url = config_service.get_setting_value("ai_endpoint")
        self.api_key = config_service.get_setting_value("ai_key")
        self.base_llm = config_service.get_setting_value("base_llm")
        self.temperature = config_service.get_setting_value("temperature")
        self.system_note = config_service.get_setting_value("system_note")

        # # Business Logic: Ensure critical configuration is set before proceeding.
        # if not self.base_url or not self.api_key or not self.base_llm:
        #     raise HTTPException(
        #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        #         detail="AI service is not configured. Please set AI endpoint, key, and base LLM in settings."
        #     )

    def _get_client(self, prompt: Prompt) -> AsyncOpenAI:
        """Helper to create an AsyncOpenAI client with prompt-specific overrides."""
        return AsyncOpenAI(
            base_url=prompt.endpoint or self.base_url,
            api_key=prompt.ai_key or self.api_key,
        )

    async def generate_response(self, prompt: Prompt) -> str:
        """
        Generates a single, non-streaming response based on a Prompt object.
        """
        client = self._get_client(prompt)

        messages = [{"role": "system", "content": prompt.system or self.system_note}]
        if prompt.user:
            messages.append({"role": "user", "content": prompt.user})
        if prompt.assistant:
            messages.append({"role": "assistant", "content": prompt.assistant})

        completion = await client.chat.completions.create(
            model=prompt.model or self.base_llm,
            stop=prompt.stop or [],
            temperature=prompt.temp or self.temperature,
            messages=messages
        )
        
        result = completion.choices[0].message.content
        return result

    async def stream_response(self, prompt: Prompt) -> AsyncGenerator[str, None]:
        """
        Streams a response based on a Prompt object, yielding content chunks.
        """
        client = self._get_client(prompt)

        stream = await client.chat.completions.create(
            model=prompt.model or self.base_llm,
            stop=prompt.stop or [],
            temperature=prompt.temp or self.temperature,
            messages=[
                {"role": "system", "content": prompt.system or self.system_note},
                {"role": "user", "content": prompt.user or ""}
            ],
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def stream_chat(self, messages: List[Dict[str, str]], overrides: Prompt = None) -> AsyncGenerator[str, None]:
        """
        Streams a response for a given list of messages, allowing for overrides.
        This is ideal for multi-turn chat applications.
        """
        if overrides is None:
            overrides = Prompt()

        client = self._get_client(overrides)

        # Ensure a system message is present
        if not any(msg.get("role") == "system" for msg in messages):
            messages.insert(0, {"role": "system", "content": self.system_note})

        stream = await client.chat.completions.create(
            model=overrides.model or self.base_llm,
            stop=overrides.stop or [],
            temperature=overrides.temp or self.temperature,
            messages=messages,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content