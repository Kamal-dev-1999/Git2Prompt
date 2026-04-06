"""
OpenRouter Blueprint Service
Sends assembled source context to OpenRouter (defaulting to Claude 3.5 Sonnet) 
and streams the generated Master Blueprint back.
"""

import httpx
from typing import AsyncGenerator
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

# We reuse the exact same prompt engineering required to command the AI
from services.gemini_blueprint import BLUEPRINT_SYSTEM_INSTRUCTION

async def generate_blueprint_stream(
    source_context: str,
    repo_name: str,
    repo_description: str,
    repo_language: str,
    api_key: str,
    base_url: str = "https://openrouter.ai/api/v1",
    model: str = "anthropic/claude-sonnet-4.5",
) -> AsyncGenerator[str, None]:
    """
    Generate a Master Blueprint via OpenAI-compatible streaming API.
    Yields chunks of the blueprint as they are generated.
    """
    client = AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    user_prompt = f"""Analyze the following codebase and generate a complete Master Blueprint Prompt.

Repository: {repo_name}
Description: {repo_description or "No description provided"}
Primary Language: {repo_language or "Not specified"}

===== SOURCE CODE CONTEXT =====
{source_context}
===== END SOURCE CODE CONTEXT =====

Generate the Master Blueprint now. Be thorough and specific."""

    messages = [
        {"role": "system", "content": BLUEPRINT_SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response_stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.3,
            max_tokens=8192,
            top_p=0.95,
        )

        async for chunk in response_stream:
            # Safely navigate the delta content
            if len(chunk.choices) > 0:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
                    
    except Exception as e:
        logger.error(f"OpenRouter streaming error: {str(e)}")
        raise e

async def generate_blueprint_sync(
    source_context: str,
    repo_name: str,
    repo_description: str,
    repo_language: str,
    api_key: str,
    base_url: str = "https://openrouter.ai/api/v1",
    model: str = "anthropic/claude-3.5-sonnet",
) -> str:
    """
    Fallback synchronous generation (yields the entire string at once)
    """
    client = AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    
    user_prompt = f"""Analyze the following codebase and generate a complete Master Blueprint Prompt.

Repository: {repo_name}
Description: {repo_description or "No description provided"}
Primary Language: {repo_language or "Not specified"}

===== SOURCE CODE CONTEXT =====
{source_context}
===== END SOURCE CODE CONTEXT =====

Generate the Master Blueprint now."""

    messages = [
        {"role": "system", "content": BLUEPRINT_SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
            temperature=0.3,
            max_tokens=8192,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenRouter sync error: {str(e)}")
        raise e
