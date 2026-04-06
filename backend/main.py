"""
RepoBlueprint Backend — FastAPI Application
Main entry point with SSE streaming endpoint for repository analysis.
"""

import os
import re
import json
import asyncio
from typing import Optional

import httpx
import logging

# Configure basic console logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from services.github_grabber import get_repo_tree, get_file_contents
from services.context_manager import build_source_context, estimate_tokens
from services.gemini_blueprint import (
    configure_gemini,
    generate_blueprint_stream,
    generate_blueprint_sync,
)

# Load environment variables
load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Initialize FastAPI
app = FastAPI(
    title="RepoBlueprint API",
    description="Analyze GitHub repositories and generate AI-ready blueprints",
    version="1.0.0",
)

# CORS — allow local Next.js frontend and deployed domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://git2-prompt.vercel.app",
        "https://git2-prompt-git-main-kamal-tripathis-projects.vercel.app",
        "https://git2-prompt-3t8hppxmk-kamal-tripathis-projects.vercel.app",
        "https://kamal.software",
        "https://www.kamal.software",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================
# Request / Response Models
# ================================

class AnalyzeRequest(BaseModel):
    repo_url: str


# ================================
# Helpers
# ================================

def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo from a GitHub URL."""
    patterns = [
        r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"github\.com/([^/]+)/([^/]+?)/?$",
        r"^([^/]+)/([^/]+)$",
    ]
    for pattern in patterns:
        match = re.match(pattern, url.strip())
        if match:
            return match.group(1), match.group(2)
    raise ValueError(f"Invalid GitHub URL: {url}")


def sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# ================================
# Rate Limiter definitions
# ================================
RATE_LIMIT_WINDOW = 600  # 10 minutes
MAX_REQUESTS = 3
ip_request_counts = {}

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    # Clean up old timestamps
    timestamps = [t for t in ip_request_counts.get(ip, []) if now - t < RATE_LIMIT_WINDOW]
    timestamps.append(now)
    ip_request_counts[ip] = timestamps
    return len(timestamps) > MAX_REQUESTS

# ================================
# SSE Analysis Endpoint
# ================================

@app.post("/api/analyze")
async def analyze_repository(request: Request, body: AnalyzeRequest):
    """
    Analyze a GitHub repository and stream progress via SSE.

    SSE Events:
      - progress: { step, message, detail }
      - blueprint: { content }
      - error: { message }
      - done: {}
    """
    # Check By-Pass Header
    user_gemini_key = request.headers.get("x-user-gemini-key", "").strip()

    # Rate Limiting
    client_ip = request.client.host if request.client else "unknown"
    if not user_gemini_key and is_rate_limited(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please wait or use your own API key to bypass."
            }
        )

    # Validate GitHub URL
    try:
        owner, repo = parse_github_url(body.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def event_stream():
        try:
            # Step 1: Fetch repo tree
            yield sse_event("progress", {
                "step": "CLONING_TREE",
                "message": f"[GIT] CONNECTING TO github.com/{owner}/{repo}...",
                "detail": "",
            })
            await asyncio.sleep(0.3)

            yield sse_event("progress", {
                "step": "CLONING_TREE",
                "message": "[GIT] FETCHING REPOSITORY TREE (RECURSIVE)...",
                "detail": "",
            })

            tree_result = await get_repo_tree(
                owner, repo,
                github_token=GITHUB_TOKEN if GITHUB_TOKEN else None,
            )

            total = tree_result["total_objects"]
            filtered = tree_result["filtered_files"]
            excluded = tree_result["excluded_count"]
            repo_name = tree_result["repo_name"]
            repo_desc = tree_result.get("description", "")
            repo_lang = tree_result.get("language", "")

            yield sse_event("progress", {
                "step": "TREE_RECEIVED",
                "message": f"[GIT] TREE RECEIVED: {total:,} OBJECTS FOUND",
                "detail": f"Repository: {repo_name}",
            })
            await asyncio.sleep(0.2)

            # Step 2: Filter files
            yield sse_event("progress", {
                "step": "FILTERING",
                "message": "[FLT] APPLYING EXCLUSION FILTERS...",
                "detail": "Excluding: node_modules, .git, lockfiles, binaries",
            })
            await asyncio.sleep(0.3)

            yield sse_event("progress", {
                "step": "FILTERING",
                "message": f"[FLT] FILTERED: {total:,} → {len(filtered):,} FILES REMAINING",
                "detail": f"Excluded {excluded:,} files",
            })
            await asyncio.sleep(0.2)

            if not filtered:
                yield sse_event("error", {
                    "message": "No analyzable files found after filtering. The repository may be empty or contain only binary files."
                })
                return

            # Step 3: Fetch file contents
            file_paths = [f["path"] for f in filtered]

            yield sse_event("progress", {
                "step": "FETCHING",
                "message": f"[CTX] FETCHING SOURCE CODE ({len(file_paths):,} FILES)...",
                "detail": "Concurrent fetch with rate limiting",
            })

            file_contents = await get_file_contents(
                owner, repo, file_paths,
                github_token=GITHUB_TOKEN if GITHUB_TOKEN else None,
            )

            yield sse_event("progress", {
                "step": "FETCHING_DONE",
                "message": f"[CTX] FETCHED {len(file_contents):,} FILES SUCCESSFULLY",
                "detail": "",
            })
            await asyncio.sleep(0.2)

            # Step 4: Build source context
            yield sse_event("progress", {
                "step": "ASSEMBLING",
                "message": "[CTX] ASSEMBLING SOURCE CONTEXT...",
                "detail": "Prioritizing config → entry points → core logic",
            })

            context_result = build_source_context(file_contents)
            total_tokens = context_result["total_tokens"]

            yield sse_event("progress", {
                "step": "ASSEMBLED",
                "message": f"[CTX] ASSEMBLED {context_result['files_included']:,} FILES → {total_tokens:,} TOKENS",
                "detail": f"Truncated: {context_result['files_truncated']} files" if context_result['files_truncated'] else "All files included fully",
            })
            await asyncio.sleep(0.2)

            effective_key = user_gemini_key if user_gemini_key else GEMINI_API_KEY
            if not effective_key:
                # Mock mode when no API key is set at all
                yield sse_event("progress", {
                    "step": "AI_MOCK",
                    "message": "[AI] GEMINI API KEY NOT SET — USING MOCK MODE",
                    "detail": "Set GEMINI_API_KEY in .env or provide your personal key to enable real analysis",
                })
                await asyncio.sleep(0.5)

                mock_blueprint = _generate_mock_blueprint(repo_name, repo_desc, repo_lang, filtered, total_tokens)
                yield sse_event("blueprint", {"content": mock_blueprint})
                yield sse_event("done", {})
                return

            if user_gemini_key:
                yield sse_event("progress", {
                    "step": "AI_USER_KEY",
                    "message": "[AI] USING PERSONAL API KEY -> RATE LIMITS BYPASSED",
                    "detail": "Your private Gemini API key is powering this analysis.",
                })
            else:
                logger.info(f"Analysis triggered using SERVER API KEY for repo {owner}/{repo}")
                yield sse_event("progress", {
                    "step": "AI_SERVER_KEY",
                    "message": "[AI] USING SERVER API KEY -> STANDARD RATE LIMITS APPLY",
                    "detail": f"Server Key Loaded. Wait time applies after {MAX_REQUESTS} requests.",
                })
            await asyncio.sleep(0.3)
            
            configure_gemini(effective_key)

            yield sse_event("progress", {
                "step": "AI_ACTIVATED",
                "message": "[AI] GEMINI 1.5 PRO ENGINE: ACTIVATED",
                "detail": f"Context: {total_tokens:,} tokens / 2,000,000 capacity",
            })
            await asyncio.sleep(0.2)

            yield sse_event("progress", {
                "step": "SYNTHESIZING",
                "message": "[AI] SYNTHESIZING MASTER BLUEPRINT...",
                "detail": "This may take 30-120 seconds for large repos",
            })

            # Stream blueprint from Gemini
            full_blueprint = ""
            try:
                async for chunk in generate_blueprint_stream(
                    source_context=context_result["context"],
                    repo_name=repo_name,
                    repo_description=repo_desc,
                    repo_language=repo_lang,
                ):
                    full_blueprint += chunk
                    yield sse_event("blueprint_chunk", {"chunk": chunk})

            except Exception as gemini_error:
                error_str = str(gemini_error).lower()
                if "api key" in error_str or "unauthorized" in error_str or "400" in error_str or "401" in error_str or "key" in error_str:
                    logger.error(f"Invalid API Key encountered! ({'PERSONAL' if user_gemini_key else 'SERVER'} KEY) - Error: {str(gemini_error)}")
                    yield sse_event("error", {
                        "message": f"[ERROR] 401 Unauthorized: Invalid Gemini API Key. Please click the Settings gear to check your Private Key.",
                        "code": 401
                    })
                    return

                # Fallback to sync if streaming fails for other reasons
                logger.warning(f"Streaming failed, switching to sync mode: {str(gemini_error)}")
                yield sse_event("progress", {
                    "step": "AI_FALLBACK",
                    "message": "[AI] SWITCHING TO SYNC MODE...",
                    "detail": str(gemini_error),
                })

                full_blueprint = generate_blueprint_sync(
                    source_context=context_result["context"],
                    repo_name=repo_name,
                    repo_description=repo_desc,
                    repo_language=repo_lang,
                )

            yield sse_event("progress", {
                "step": "COMPLETE",
                "message": f"[AI] BLUEPRINT GENERATION COMPLETE ✓",
                "detail": f"{len(full_blueprint.split()):,} words generated",
            })
            await asyncio.sleep(0.2)

            yield sse_event("blueprint", {"content": full_blueprint})
            yield sse_event("done", {})
            logger.info("Analysis completed successfully.")

        except httpx_errors as e:
            logger.error(f"GitHub API Error: {str(e)}")
            yield sse_event("error", {
                "message": f"GitHub API error: {str(e)}"
            })
        except Exception as e:
            logger.error(f"Unexpected Analysis Exception: {str(e)}", exc_info=True)
            yield sse_event("error", {
                "message": f"Analysis failed: {str(e)}"
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ================================
# Health Check & Root
# ================================

@app.get("/")
async def root():
    return {
        "message": "RepoBlueprint Backend is running!",
        "status": "online",
        "endpoints": ["/api/analyze", "/api/health"]
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "gemini_configured": bool(GEMINI_API_KEY),
        "github_token_configured": bool(GITHUB_TOKEN),
    }


# ================================
# Mock Blueprint Generator
# ================================

def _generate_mock_blueprint(
    repo_name: str,
    description: str,
    language: str,
    filtered_files: list[dict],
    total_tokens: int,
) -> str:
    """Generate a mock blueprint when Gemini API key is not set."""
    file_tree = "\n".join(f"  {f['path']}" for f in filtered_files[:50])
    if len(filtered_files) > 50:
        file_tree += f"\n  ... and {len(filtered_files) - 50} more files"

    return f"""# Master Blueprint: {repo_name}

> **Note:** This is a MOCK blueprint generated without Gemini AI.
> Set your `GEMINI_API_KEY` in `backend/.env` to enable real AI-powered analysis.

## 1. Project Overview
**Repository:** {repo_name}
**Description:** {description or "No description provided"}
**Primary Language:** {language or "Not specified"}
**Files Analyzed:** {len(filtered_files):,}
**Total Tokens:** {total_tokens:,}

## 2. Repository File Tree (Filtered)
```
{file_tree}
```

## 3. Analysis Summary
This repository contains **{len(filtered_files):,} analyzable files** across approximately **{total_tokens:,} tokens** of source code.

To generate a real, detailed blueprint with:
- Component & module breakdown
- Inter-component data flow analysis
- Step-by-step implementation guide
- Architecture patterns identification

**Configure your Gemini API key:**
1. Get a key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Copy `backend/.env.example` to `backend/.env`
3. Set `GEMINI_API_KEY=your_key_here`
4. Restart the backend server

## 4. Files Detected
The following file types were found:
{_summarize_file_types(filtered_files)}

---
*Blueprint generated by RepoBlueprint v1.0 (Mock Mode)*
"""


def _summarize_file_types(files: list[dict]) -> str:
    """Summarize file types found in the repository."""
    ext_counts: dict[str, int] = {}
    for f in files:
        parts = f["path"].rsplit(".", 1)
        ext = f".{parts[1]}" if len(parts) > 1 else "no extension"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    sorted_exts = sorted(ext_counts.items(), key=lambda x: -x[1])
    lines = []
    for ext, count in sorted_exts[:15]:
        lines.append(f"- `{ext}`: {count} files")
    if len(sorted_exts) > 15:
        lines.append(f"- ... and {len(sorted_exts) - 15} more types")
    return "\n".join(lines)


httpx_errors = (httpx.HTTPStatusError, httpx.RequestError)


# ================================
# Run with Uvicorn
# ================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
