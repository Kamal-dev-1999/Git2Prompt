"""
GitHub Grabber Service
Fetches repository tree and file contents via GitHub REST API.
Applies strict filtering to exclude irrelevant files.
"""

import httpx
import base64
import asyncio
from typing import Optional

# ================================
# EXCLUSION FILTERS
# ================================

EXCLUDED_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", "__pycache__",
    ".venv", "venv", "vendor", ".cache", ".turbo", "coverage",
    ".nyc_output", ".parcel-cache", ".svn", ".hg", "bower_components",
    "jspm_packages", ".gradle", ".idea", ".vscode", ".vs",
    "target", "out", "bin", "obj", ".terraform", ".serverless",
    ".vercel", ".netlify", "storybook-static", "cypress/videos",
    "cypress/screenshots", ".docusaurus", ".nuxt", ".output",
}

EXCLUDED_FILES = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb",
    "Gemfile.lock", "poetry.lock", "Pipfile.lock", "composer.lock",
    "Cargo.lock", "go.sum", ".DS_Store", "Thumbs.db", ".gitkeep",
    ".npmrc", ".yarnrc", ".editorconfig",
}

EXCLUDED_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".bmp", ".tiff", ".avif",
    # Fonts
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    # Media
    ".mp4", ".mp3", ".wav", ".ogg", ".webm", ".avi", ".mov",
    # Archives
    ".zip", ".tar", ".gz", ".bz2", ".rar", ".7z",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    # Compiled / binary
    ".pyc", ".pyo", ".class", ".o", ".so", ".dll", ".exe",
    ".wasm", ".min.js", ".min.css", ".map",
    # Data dumps
    ".sql", ".sqlite", ".db",
}

MAX_FILE_SIZE_BYTES = 100_000  # 100KB per file


def should_include_path(path: str, size: int) -> bool:
    """Determine if a file path should be included in analysis."""
    parts = path.split("/")

    # Check excluded directories
    for part in parts[:-1]:  # all directories in the path
        if part in EXCLUDED_DIRS:
            return False

    filename = parts[-1]

    # Check excluded files
    if filename in EXCLUDED_FILES:
        return False

    # Check excluded extensions
    for ext in EXCLUDED_EXTENSIONS:
        if filename.lower().endswith(ext):
            return False

    # Check file size
    if size > MAX_FILE_SIZE_BYTES:
        return False

    return True


async def get_repo_tree(
    owner: str,
    repo: str,
    github_token: Optional[str] = None,
) -> dict:
    """
    Fetch the recursive tree of a GitHub repository.
    Returns: { "total_objects": int, "filtered_files": list[dict], "excluded_count": int }
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RepoBlueprint/1.0",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get the default branch SHA
        repo_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
        )
        repo_resp.raise_for_status()
        repo_data = repo_resp.json()
        default_branch = repo_data.get("default_branch", "main")

        # Get recursive tree
        tree_resp = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1",
            headers=headers,
        )
        tree_resp.raise_for_status()
        tree_data = tree_resp.json()

    all_items = tree_data.get("tree", [])
    total_objects = len(all_items)

    # Filter to only blobs (files) that pass our filters
    filtered_files = []
    for item in all_items:
        if item.get("type") != "blob":
            continue
        path = item.get("path", "")
        size = item.get("size", 0)
        if should_include_path(path, size):
            filtered_files.append({
                "path": path,
                "size": size,
                "sha": item.get("sha", ""),
            })

    excluded_count = total_objects - len(filtered_files)

    return {
        "total_objects": total_objects,
        "filtered_files": filtered_files,
        "excluded_count": excluded_count,
        "repo_name": repo_data.get("full_name", f"{owner}/{repo}"),
        "description": repo_data.get("description", ""),
        "language": repo_data.get("language", ""),
        "default_branch": default_branch,
    }


async def get_file_contents(
    owner: str,
    repo: str,
    file_paths: list[str],
    github_token: Optional[str] = None,
    max_concurrent: int = 10,
) -> list[dict]:
    """
    Fetch the contents of multiple files from a GitHub repository.
    Returns: list[{ "path": str, "content": str, "size": int }]
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RepoBlueprint/1.0",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def fetch_single(client: httpx.AsyncClient, path: str):
        async with semaphore:
            try:
                resp = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

                content = ""
                if data.get("encoding") == "base64" and data.get("content"):
                    try:
                        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                    except Exception:
                        content = "[BINARY OR UNREADABLE CONTENT]"
                elif data.get("content"):
                    content = data["content"]

                results.append({
                    "path": path,
                    "content": content,
                    "size": len(content),
                })
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    # Rate limit hit — wait and retry once
                    await asyncio.sleep(2)
                    try:
                        resp = await client.get(
                            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                            headers=headers,
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        content = ""
                        if data.get("encoding") == "base64" and data.get("content"):
                            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                        results.append({"path": path, "content": content, "size": len(content)})
                    except Exception:
                        results.append({"path": path, "content": f"[ERROR FETCHING: {path}]", "size": 0})
                else:
                    results.append({"path": path, "content": f"[ERROR: HTTP {e.response.status_code}]", "size": 0})
            except Exception as e:
                results.append({"path": path, "content": f"[ERROR: {str(e)}]", "size": 0})

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [fetch_single(client, path) for path in file_paths]
        await asyncio.gather(*tasks)

    # Sort by path for consistent ordering
    results.sort(key=lambda x: x["path"])
    return results
