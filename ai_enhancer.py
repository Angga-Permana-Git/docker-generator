import os
import json
import random
import string
from pathlib import Path


def _build_project_structure(source_dir: str, max_depth: int = 3, max_files: int = 300) -> str:
    root = Path(source_dir)
    if not root.is_dir():
        return ""
    lines = []
    ignored = {"node_modules", "vendor", ".git", "__pycache__", ".next", "dist", "build"}
    count = 0

    def walk(directory, depth):
        nonlocal count
        if count >= max_files:
            return
        entries = sorted([e for e in directory.iterdir() if e.name not in ignored],
                         key=lambda e: (e.is_file(), e.name.lower()))
        for entry in entries:
            if count >= max_files:
                return
            count += 1
            if entry.is_dir():
                lines.append("  " * depth + entry.name + "/")
                if depth < max_depth:
                    walk(entry, depth + 1)
            else:
                lines.append("  " * depth + entry.name)

    walk(root, 0)
    return "\n".join(lines)


def _read_dependencies(source_dir: str) -> str:
    root = Path(source_dir)
    parts = []
    for name in ("requirements.txt", "package.json", "composer.json", "pyproject.toml", "Pipfile"):
        for p in root.rglob(name):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    parts.append(f"--- {name} ---\n{f.read()[:4000]}")
            except Exception:
                pass
            break
    return "\n\n".join(parts)


def _build_prompt(framework: str, source_dir: str) -> str:
    structure = _build_project_structure(source_dir)
    deps = _read_dependencies(source_dir)
    return f"""You are a Docker and DevOps expert. Analyze this {framework} project and provide recommendations.

Project structure:
{structure}

Dependencies:
{deps}

Provide your recommendations in strict JSON format only (no markdown):
{{
  "dockerfile_optimizations": ["..."],
  "environment_variables": [{{"name": "...", "value": "...", "description": "..."}}],
  "performance_suggestions": ["..."],
  "security_recommendations": ["..."]
}}
"""


def enhance_with_ai(provider: str, api_key: str, framework: str, source_dir: str) -> dict:
    prompt = _build_prompt(framework, source_dir)

    if provider.lower() == "openai":
        result = _call_openai(api_key, prompt)
    elif provider.lower() == "anthropic":
        result = _call_anthropic(api_key, prompt)
    else:
        result = _call_openai(api_key, prompt)
    return result


def _call_openai(api_key: str, prompt: str) -> dict:
    try:
        from openai import OpenAI
    except ImportError:
        return _fallback_result()
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are a Docker and DevOps expert returning strict JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception:
        return _fallback_result()


def _call_anthropic(api_key: str, prompt: str) -> dict:
    try:
        import httpx
    except ImportError:
        return _fallback_result()
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            data = resp.json()
            text = data["content"][0]["text"]
            return json.loads(text)
    except Exception:
        return _fallback_result()


def _fallback_result() -> dict:
    key = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    return {
        "dockerfile_optimizations": [
            "Gunakan multistage build untuk mengurangi ukuran image dan memisahkan build-time dari runtime dependencies."
        ],
        "environment_variables": [
            {"name": "APP_ENV", "value": "production", "description": "Menandakan mode production."},
            {"name": "APP_DEBUG", "value": "false", "description": "Nonaktifkan debug di production."},
        ],
        "performance_suggestions": [
            "Gunakan caching di layer Docker untuk mempercepat build (copy dependency files sebelum source code)."
        ],
        "security_recommendations": [
            "Jalankan container sebagai non-root user dan gunakan read-only filesystem.",
            "Gunakan secret management dan jangan hardcode credentials di image.",
        ],
        "_note": "AI analysis gagal dihubungi; menggunakan rekomendasi standar. Reference: " + key,
    }
