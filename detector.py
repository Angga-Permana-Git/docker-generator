import json
from pathlib import Path


FRAMEWORKS = {
    "nextjs": {
        "framework": "nextjs",
        "label": "Next.js",
        "default_port": 3000,
        "db_suggestion": "postgresql",
        "type": "Node SSR",
    },
    "react": {
        "framework": "react",
        "label": "React.js",
        "default_port": 80,
        "db_suggestion": "none",
        "type": "Static Build",
    },
    "express": {
        "framework": "nodeexpress",
        "label": "Node/Express",
        "default_port": 3000,
        "db_suggestion": "postgresql",
        "type": "Node Backend",
    },
    "laravel": {
        "framework": "laravel",
        "label": "Laravel",
        "default_port": 9000,
        "db_suggestion": "mysql",
        "type": "PHP-FPM",
    },
    "codeigniter4": {
        "framework": "codeigniter4",
        "label": "CodeIgniter 4",
        "default_port": 8080,
        "db_suggestion": "mysql",
        "type": "PHP-FPM",
    },
    "codeigniter3": {
        "framework": "codeigniter3",
        "label": "CodeIgniter 3",
        "default_port": 8080,
        "db_suggestion": "mysql",
        "type": "PHP-FPM",
    },
    "django": {
        "framework": "django",
        "label": "Django",
        "default_port": 8000,
        "db_suggestion": "postgresql",
        "type": "Python WSGI",
    },
    "fastapi": {
        "framework": "fastapi",
        "label": "FastAPI",
        "default_port": 8000,
        "db_suggestion": "postgresql",
        "type": "Python ASGI",
    },
    "flask": {
        "framework": "flask",
        "label": "Flask",
        "default_port": 5000,
        "db_suggestion": "postgresql",
        "type": "Python WSGI",
    },
    "generic": {
        "framework": "generic",
        "label": "Generic",
        "default_port": 8080,
        "db_suggestion": "none",
        "type": "Fallback",
    },
}


def _read_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return json.load(f)
    except Exception:
        return None


def _read_text(path: Path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().lower()
    except Exception:
        return ""


def detect_framework(source_dir: str) -> dict:
    root = Path(source_dir)
    if not root.is_dir():
        return dict(FRAMEWORKS["generic"])

    # 1. PHP ecosystem
    # Checked before Node because PHP projects (Laravel, CodeIgniter) commonly
    # ship a package.json that only contains frontend build tooling (Vite,
    # Tailwind, axios). Those must not override the real PHP backend detection.
    composer = _find(root, "composer.json")
    if composer:
        data = _read_json(composer)
        req = {}
        if data:
            req = {
                **(data.get("require") or {}),
                **(data.get("require-dev") or {}),
            }
        req_str = json.dumps(req).lower()
        if "laravel/framework" in req_str:
            return dict(FRAMEWORKS["laravel"])
        if "codeigniter4/framework" in req_str:
            return dict(FRAMEWORKS["codeigniter4"])
        return dict(FRAMEWORKS["laravel"])

    # 2. Node.js ecosystem
    pkg_json = _find(root, "package.json")
    if pkg_json:
        data = _read_json(pkg_json)
        deps = {}
        if data:
            deps = {
                **(data.get("dependencies") or {}),
                **(data.get("devDependencies") or {}),
            }
        dep_str = json.dumps(deps).lower()
        if "next" in dep_str:
            return dict(FRAMEWORKS["nextjs"])
        if "express" in dep_str or "@nestjs/core" in dep_str:
            return dict(FRAMEWORKS["express"])
        if "react" in dep_str or "vue" in dep_str or "angular" in dep_str:
            return dict(FRAMEWORKS["react"])
        return dict(FRAMEWORKS["express"])

    # 3. Python ecosystem
    req_txt = _find(root, "requirements.txt")
    pyproject = _find(root, "pyproject.toml")
    if req_txt:
        content = _read_text(req_txt)
        if "django" in content:
            return dict(FRAMEWORKS["django"])
        if "fastapi" in content:
            return dict(FRAMEWORKS["fastapi"])
        if "flask" in content:
            return dict(FRAMEWORKS["flask"])
    if pyproject:
        content = _read_text(pyproject)
        if "django" in content:
            return dict(FRAMEWORKS["django"])
        if "fastapi" in content:
            return dict(FRAMEWORKS["fastapi"])
        if "flask" in content:
            return dict(FRAMEWORKS["flask"])

    # 4. CodeIgniter 3 folder structure
    if (root / "application").is_dir() and (root / "system").is_dir():
        return dict(FRAMEWORKS["codeigniter3"])

    # 5. Ultimate fallback
    return dict(FRAMEWORKS["generic"])


def _find(root: Path, filename: str):
    for p in root.rglob(filename):
        return p
    return None
