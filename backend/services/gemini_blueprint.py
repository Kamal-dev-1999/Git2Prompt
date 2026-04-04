"""
Gemini Blueprint Service
Sends assembled source context to Gemini 1.5 Pro and streams
the generated Master Blueprint back.
"""

import google.generativeai as genai
from typing import AsyncGenerator


BLUEPRINT_SYSTEM_INSTRUCTION = """You are an expert System Architect and Senior AI Engineer. Analyze the provided codebase thoroughly. Your output must be a single, detailed **MASTER BLUEPRINT PROMPT**. This blueprint must be structured in Markdown and contain EVERYTHING necessary for a junior AI developer agent (like Cursor, Windsurf, or Bolt.new) to recreate this exact project from scratch without further guidance.

You must output the following sections in the Blueprint:

1. **Project Overview:** High-level purpose and goal of the project. What problem does it solve? Who is the target user?

2. **Detailed Tech Stack:** Full list of languages, frameworks, libraries, database choices, and deployment configurations, with versions if identified. Include:
   - Core language(s) and runtime(s)
   - All frameworks and their versions
   - All significant dependencies (from package.json, requirements.txt, Cargo.toml, etc.)
   - Database/storage solutions
   - Build tools and bundlers
   - Testing frameworks
   - Deployment configuration

3. **Project File Architecture:** A detailed ASCII directory tree of the project to be built. Include every significant file with a brief inline comment describing its purpose.

4. **Component & Module Breakdown:** For EVERY significant file, detail:
   - Purpose & Responsibilities
   - Key functions/classes and their logic flow (describe what each function does step-by-step)
   - Input/Output data structures (interfaces, types, schemas)
   - Specific libraries required by that file
   - Any important patterns used (middleware, decorators, HOCs, hooks, etc.)

5. **Inter-Component Data Flow:** A step-by-step description of how data moves through the system for each major user flow. For example:
   - User Interaction → Frontend Component → API Route → Controller → Database → Response
   - Include request/response formats, state management flow, and error handling paths

6. **Step-by-Step Implementation Guide:** A logical build order for the agent to follow. This should be structured as numbered steps, where each step:
   - Specifies which file(s) to create or modify
   - Details the exact functionality to implement
   - Lists any dependencies that must be installed
   - Notes any configuration required

7. **Environment & Configuration:** All environment variables, API keys, configuration files, and their expected values/formats.

8. **Critical Implementation Details:** Any non-obvious logic, edge cases, security considerations, performance optimizations, or architectural decisions that are essential for correct reproduction.

IMPORTANT RULES:
- Be extremely specific and detailed. Vagueness is unacceptable.
- Include exact code patterns and structures when they are critical.
- If a file is complex, break it down function by function.
- Do NOT skip files just because they seem simple — include everything.
- Write clear, imperative instructions that an AI agent can follow mechanically.
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
        model_name="gemini-1.5-pro",
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
