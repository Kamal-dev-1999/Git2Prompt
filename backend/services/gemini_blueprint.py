"""
Gemini Blueprint Service
Sends assembled source context to Gemini 1.5 Pro and streams
the generated Master Blueprint back.
"""

import google.generativeai as genai
from typing import AsyncGenerator


BLUEPRINT_SYSTEM_INSTRUCTION = """You are an expert Prompt Engineer and Senior AI Architect. Analyze the provided codebase thoroughly. Your sole objective is to output a single, hyper-detailed **MASTER PROMPT**. This Master Prompt must be written entirely from the perspective of instructing another AI assistant (like Cursor, Windsurf, or Bolt) to build the identical project from scratch.

Crucially, DO NOT explain the project to me. Instead, output the exact command and instructions I will copy-paste to another AI.

Begin your output directly with the Prompt payload. For example: "You are an expert Full-Stack developer. Your task is to build a project called X. Below is the strict architecture, stack, and step-by-step instructions you must follow... "

Ensure the generated Master Prompt contains the following sections:

1. **System Persona & Objective:** Formally instruct the target AI on its role and its exact goal. Include the core functionality of the app based on your analysis.
2. **Tech Stack & Libraries:** Instruct the AI on exactly which languages, frameworks, UI libraries, database solutions, and dependencies to install and use. Be precise about versions if known.
3. **Project Architecture:** Provide an ASCII directory tree as a strict structural constraint for the AI to follow.
4. **File-by-File Implementation Steps:** A deeply specific, numbered list of imperative commands instructing the AI on exactly what files to create and what logic/code to write in each file. Include input/output data structures, component responsibilities, and how they interact. Don't skip files.
5. **Rules & Constraints:** Any critical edge cases, styling nuances, performance optimizations, and deployment configurations the AI must obey while building.

IMPORTANT RULES:
- Your entire response must ONLY be the payload of the prompt directed at the target AI. Do not include introductory text like "Here is the master prompt".
- Be authoritative and use imperative verbs ("Build this", "Use that", "Implement X").
- Be extremely specific. Generalizations will cause the target AI to hallucinate. Provide concrete logic requirements for every significant file.
"""


def configure_gemini(api_key: str):
    """Configure the Gemini API with the provided key."""
    genai.configure(api_key=api_key)


def generate_blueprint_sync(
    source_context: str,
    repo_name: str,
    repo_description: str,
    repo_language: str,
) -> str:
    """
    Generate a Master Blueprint synchronously.
    Returns the complete blueprint as a string.
    """
    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=BLUEPRINT_SYSTEM_INSTRUCTION,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 8192,
            "top_p": 0.95,
        },
    )

    user_prompt = f"""Analyze the following codebase and generate a complete Master Blueprint Prompt.

Repository: {repo_name}
Description: {repo_description or "No description provided"}
Primary Language: {repo_language or "Not specified"}

===== SOURCE CODE CONTEXT =====
{source_context}
===== END SOURCE CODE CONTEXT =====

Generate the Master Blueprint now. Be thorough and specific."""

    response = model.generate_content(user_prompt)
    return response.text


async def generate_blueprint_stream(
    source_context: str,
    repo_name: str,
    repo_description: str,
    repo_language: str,
) -> AsyncGenerator[str, None]:
    """
    Generate a Master Blueprint with streaming.
    Yields chunks of the blueprint as they are generated.
    """
    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=BLUEPRINT_SYSTEM_INSTRUCTION,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 8192,
            "top_p": 0.95,
        },
    )

    user_prompt = f"""Analyze the following codebase and generate a complete Master Blueprint Prompt.

Repository: {repo_name}
Description: {repo_description or "No description provided"}
Primary Language: {repo_language or "Not specified"}

===== SOURCE CODE CONTEXT =====
{source_context}
===== END SOURCE CODE CONTEXT =====

Generate the Master Blueprint now. Be thorough and specific."""

    response = model.generate_content(user_prompt, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text
