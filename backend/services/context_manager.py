"""
Context Manager Service
Assembles fetched file contents into a single source context block
for feeding to the Gemini LLM.
"""


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)."""
    return len(text) // 4


# Priority tiers for file inclusion when token budget is tight
PRIORITY_TIERS = {
    "config": [
        "package.json", "tsconfig.json", "next.config", "vite.config",
        "tailwind.config", "postcss.config", "webpack.config",
        "Cargo.toml", "go.mod", "pyproject.toml", "setup.py", "setup.cfg",
        "requirements.txt", "Gemfile", "build.gradle", "pom.xml",
        "Makefile", "Dockerfile", "docker-compose", ".env.example",
        "README.md", "readme.md",
    ],
    "entry": [
        "main.", "index.", "app.", "server.", "mod.rs", "lib.rs",
        "__init__.", "manage.py", "wsgi.", "asgi.",
    ],
    "core": [
        "src/", "lib/", "app/", "pages/", "components/", "services/",
        "controllers/", "handlers/", "routes/", "api/", "models/",
        "utils/", "helpers/", "hooks/", "store/", "middleware/",
    ],
    "tests": [
        "test", "spec", "__tests__", "tests/",
    ],
    "docs": [
        "docs/", "doc/", ".md",
    ],
}


def get_file_priority(path: str) -> int:
    """
    Return priority score (lower = higher priority).
    0 = config, 1 = entry, 2 = core, 3 = tests, 4 = docs, 5 = other.
    """
    path_lower = path.lower()

    for i, (tier_name, patterns) in enumerate(PRIORITY_TIERS.items()):
        for pattern in patterns:
            if pattern in path_lower:
                return i

    return 5  # Other


def build_source_context(
    files: list[dict],
    max_tokens: int = 1_800_000,
) -> dict:
    """
    Assemble file contents into a single source context block.

    Args:
        files: List of { "path": str, "content": str, "size": int }
        max_tokens: Maximum token budget (default 1.8M to leave room for prompt)

    Returns:
        { "context": str, "total_tokens": int, "files_included": int, "files_truncated": int }
    """
    # Sort files by priority
    prioritized = sorted(files, key=lambda f: (get_file_priority(f["path"]), f["path"]))

    context_parts = []
    total_chars = 0
    files_included = 0
    files_truncated = 0
    char_budget = max_tokens * 4  # Convert token budget to char budget

    for file_info in prioritized:
        path = file_info["path"]
        content = file_info["content"]

        if not content or content.startswith("[ERROR"):
            continue

        # Build the file block
        separator = f"\n{'='*60}\n--- FILE: {path} ---\n{'='*60}\n"
        file_block = separator + content + "\n"

        block_chars = len(file_block)

        # Check if we can fit this file
        if total_chars + block_chars > char_budget:
            # Try truncating the content
            remaining = char_budget - total_chars - len(separator) - 100
            if remaining > 500:  # Only include if we can fit at least 500 chars
                truncated_content = content[:remaining] + "\n\n[... TRUNCATED DUE TO TOKEN LIMIT ...]"
                file_block = separator + truncated_content + "\n"
                context_parts.append(file_block)
                total_chars += len(file_block)
                files_included += 1
                files_truncated += 1
            break  # Stop adding more files
        else:
            context_parts.append(file_block)
            total_chars += block_chars
            files_included += 1

    full_context = "".join(context_parts)
    total_tokens = estimate_tokens(full_context)

    return {
        "context": full_context,
        "total_tokens": total_tokens,
        "files_included": files_included,
        "files_truncated": files_truncated,
    }
