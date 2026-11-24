from __future__ import annotations

import fnmatch
import os
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from .documents import slugify

CONFIG_NAME = ".agent-engineering.yaml"
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "bin", "obj",
    "dist", "build", "target", ".next", ".cache", "__pycache__",
}
LANGUAGES = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".java": "java", ".kt": "kotlin",
    ".cs": "csharp", ".fs": "fsharp", ".go": "go", ".rs": "rust", ".rb": "ruby",
    ".php": "php", ".swift": "swift", ".c": "c", ".h": "c", ".cpp": "cpp",
    ".hpp": "cpp", ".scala": "scala", ".ex": "elixir", ".dart": "dart",
}
INSTRUCTION_FILES = [
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules", ".windsurfrules",
    ".github/copilot-instructions.md", ".github/instructions",
    ".cursor/rules", ".agent/instructions.md",
]


def load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_NAME
    if not path.exists():
        raise ValueError(f"Missing {CONFIG_NAME}. Run 'aeng discover' or create it from the template.")
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    validate_config(data)
    return data


def validate_config(config: dict[str, Any]) -> None:
    if config.get("version") != 1:
        raise ValueError("config.version must be 1")
    project = config.get("project")
    if not isinstance(project, dict) or not project.get("name"):
        raise ValueError("project.name is required")
    if not isinstance(project.get("languages"), list) or not project["languages"]:
        raise ValueError("project.languages must be a non-empty list")
    modules = config.get("modules")
    if not isinstance(modules, list) or not modules:
        raise ValueError("modules must be a non-empty list")
    seen: set[str] = set()
    for module in modules:
        if not isinstance(module, dict):
            raise ValueError("each module must be a mapping")
        module_id = module.get("id")
        if not module_id or module_id in seen:
            raise ValueError(f"duplicate or empty module id: {module_id!r}")
        if not isinstance(module.get("paths"), list) or not module["paths"]:
            raise ValueError(f"module {module_id}: paths must be a non-empty list")
        seen.add(module_id)
    test = config.get("test")
    if not isinstance(test, dict) or not isinstance(test.get("default_command"), str):
        raise ValueError("test.default_command is required (use an empty string if unknown)")
    verification = config.get("verification", {})
    if not isinstance(verification.get("stale_days", 30), int):
        raise ValueError("verification.stale_days must be an integer")


def matches(path: str, pattern: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return fnmatch.fnmatchcase(normalized, pattern.replace("\\", "/"))


def path_matches_any(path: str, patterns: list[str]) -> bool:
    return any(matches(path, pattern) for pattern in patterns)


def _walk(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".aeng"))
        for name in sorted(files):
            yield Path(current) / name


def _detect_test_command(root: Path, source_roots: list[str]) -> str:
    if (root / "package.json").exists():
        return "npm test"
    if (root / "Cargo.toml").exists():
        return "cargo test"
    if (root / "go.mod").exists():
        return "go test ./..."
    if (root / "pom.xml").exists():
        return "mvn test"
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        return "gradle test"
    solutions = sorted(root.glob("*.slnx")) + sorted(root.glob("*.sln"))
    if solutions:
        return f"dotnet test {solutions[0].name}"
    if (root / "pyproject.toml").exists():
        text = (root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore").lower()
        return "python -m pytest -q" if "pytest" in text else "python -m unittest discover -s tests -v"
    if (root / "pytest.ini").exists() or (root / "tox.ini").exists():
        return "python -m pytest -q"
    if (root / "tests").exists() or any((root / item / "tests").exists() for item in source_roots):
        return "python -m unittest discover -s tests -v"
    return ""


def discover(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = list(_walk(root))
    counts = Counter(LANGUAGES[path.suffix.lower()] for path in files if path.suffix.lower() in LANGUAGES)
    languages = [language for language, _ in counts.most_common()]
    common_roots = ["src", "source", "lib", "app", "server", "packages"]
    source_roots = [item for item in common_roots if (root / item).is_dir()]
    if not source_roots:
        source_roots = ["src"] if (root / "src").is_dir() else ["."]

    modules: list[dict[str, Any]] = []
    used: set[str] = set()
    for source_root in source_roots:
        base = root / source_root
        if not base.is_dir():
            continue
        children = [item for item in sorted(base.iterdir()) if item.is_dir() and item.name not in SKIP_DIRS]
        code_children = [item for item in children if any(path.suffix.lower() in LANGUAGES for path in _walk(item))]
        if not code_children:
            candidates = [base]
        else:
            candidates = code_children[:12]
        for candidate in candidates:
            module_id = slugify(candidate.name if candidate != base else (root.name if source_root == "." else source_root))
            unique = module_id
            suffix = 2
            while unique in used:
                unique = f"{module_id}-{suffix}"
                suffix += 1
            used.add(unique)
            relative = candidate.relative_to(root).as_posix()
            pattern = f"{relative}/**" if candidate != base else "**/*"
            modules.append({
                "id": unique,
                "name": candidate.name.replace("-", " ").replace("_", " ").title() if candidate != base else "Application",
                "paths": [pattern],
                "responsibility": "Review and describe this module's responsibility.",
            })

    if not modules:
        modules = [{"id": "application", "name": "Application", "paths": ["**/*"], "responsibility": "Review and describe this module."}]

    docs_root = next((name for name in ["docs", "documentation", "doc"] if (root / name).is_dir()), "docs")
    existing = [name for name in INSTRUCTION_FILES if (root / name).exists()]
    default_command = _detect_test_command(root, source_roots)
    return {
        "version": 1,
        "project": {
            "name": root.name,
            "description": "Describe the project purpose.",
            "languages": languages or ["unknown"],
            "documentation_languages": ["en"],
            "source_roots": source_roots,
            "docs_root": docs_root,
        },
        "modules": modules,
        "test": {
            "default_command": default_command,
            "fast_command": default_command,
            "full_command": default_command,
            "areas": {module["id"]: module["paths"] for module in modules},
            "area_commands": {},
            "broad_change": {
                "paths": ["pyproject.toml", "package.json", "Cargo.toml", "go.mod", "Makefile", "*.sln", "*.slnx", "tests/**", "test/**"],
                "max_files": 30,
                "max_modules": 4,
            },
        },
        "verification": {
            "stale_days": 30,
            "ui": any((root / name).is_dir() for name in ["ui", "web", "frontend"]) or any(lang in languages for lang in ["javascript", "typescript"]),
        },
        "existing": {
            "agent_files": [name for name in existing if name in {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}],
            "instruction_files": [name for name in existing if name not in {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}],
            "preserve_existing": True,
        },
        "github": {
            "issue_required": True,
            "manual_test_label": "manual testing",
        },
        "discovery": {
            "generated_by": "aeng discover",
            "review_required": True,
            "languages_by_file_count": dict(counts),
        },
    }


def dump_config(config: dict[str, Any]) -> str:
    return yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
