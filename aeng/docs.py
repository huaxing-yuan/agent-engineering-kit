from __future__ import annotations

import re
import shlex
import subprocess
from collections import Counter
from datetime import date
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from .config import path_matches_any
from .documents import parse_document, parse_table, today
from .test_selector import changed_files

VALID_TECHNICAL_STATUS = {"proposed", "current", "superseded"}
VALID_SCREENSHOT_STATUS = {"placeholder", "captured", "verified", "stale", "obsolete"}


def _valid_date(value: Any) -> bool:
    try:
        date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def _resolves(root: Path, value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    if any(char in value for char in "*?["):
        return any(root.glob(value))
    return (root / value).exists()


def _markdown_files(docs_root: Path) -> list[Path]:
    return sorted(path for path in docs_root.rglob("*.md") if not path.name.startswith("_"))


def _local_links(text: str):
    text = re.sub(r"(?ms)^```.*?^```\s*$", "", text)
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0].split("?", 1)[0].strip()
        if target and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) and "{{" not in target:
            yield target


def _traceability(text: str) -> list[tuple[str, str]]:
    result = []
    for comment in re.findall(r"<!--(.*?)-->", text, re.S):
        for line in comment.splitlines():
            match = re.match(r"\s*([A-Za-z ]+Source):\s*(.+?)\s*$", line)
            if not match:
                continue
            value = re.sub(r"\s+\(\d{4}-\d{2}-\d{2}\)\s*$", "", match.group(2))
            result.append((match.group(1), value))
    return result


def _screenshot_rows(root: Path, config: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    documentation = config.get("documentation", {})
    screenshots = documentation.get("screenshots", {})
    index = screenshots.get("index")
    if not index:
        return [], []
    path = root / index
    if not path.exists():
        if screenshots.get("required"):
            return [], [f"{index}: screenshot index is missing"]
        return [], []
    headers, rows = parse_table(path.read_text(encoding="utf-8"), "Screenshots")
    if not headers:
        return [], [f"{index}: Screenshots table is missing"]
    return rows, []


def technical_notes(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    notes = []
    errors = []
    directory = root / "engineering/technical"
    for path in sorted(directory.rglob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        try:
            data, _ = parse_document(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
            continue
        required = {"id", "status", "updated", "reviewed_against", "source_paths"}
        missing = sorted(required - set(data))
        if missing:
            errors.append(f"{path.relative_to(root)}: missing technical frontmatter: {', '.join(missing)}")
        if data.get("id") != path.stem:
            errors.append(f"{path.relative_to(root)}: id must match the filename")
        if data.get("status") not in VALID_TECHNICAL_STATUS:
            errors.append(f"{path.relative_to(root)}: invalid technical status {data.get('status')!r}")
        if not _valid_date(data.get("updated")):
            errors.append(f"{path.relative_to(root)}: updated must be YYYY-MM-DD")
        if data.get("status") == "current":
            if not data.get("reviewed_against"):
                errors.append(f"{path.relative_to(root)}: current note requires reviewed_against")
            sources = data.get("source_paths", [])
            if not sources:
                errors.append(f"{path.relative_to(root)}: current note requires source_paths")
            for source in sources:
                if not _resolves(root, str(source)):
                    errors.append(f"{path.relative_to(root)}: source path does not resolve: {source}")
        if data.get("status") == "superseded" and not data.get("superseded_by"):
            errors.append(f"{path.relative_to(root)}: superseded note requires superseded_by")
        notes.append(data)
    return notes, errors


def documentation_metrics(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    documentation = config.get("documentation")
    if not documentation:
        return {"configured": False}
    docs_root = root / documentation["root"]
    pages = _markdown_files(docs_root) if docs_root.exists() else []
    by_locale = Counter()
    for page in pages:
        relative = page.relative_to(docs_root)
        by_locale[relative.parts[0] if len(relative.parts) > 1 else "root"] += 1
    rows, _ = _screenshot_rows(root, config)
    screenshot_counts = Counter(row.get("status", "unknown") for row in rows)
    technical, _ = technical_notes(root)
    technical_counts = Counter(str(note.get("status", "unknown")) for note in technical)
    doc_gaps = 0
    for card in sorted((root / "engineering/modules").glob("*.md")):
        if card.name.startswith("_"):
            continue
        doc_gaps += sum("**doc gap**" in line.lower() for line in card.read_text(encoding="utf-8-sig").splitlines())
    return {
        "configured": True,
        "root": documentation["root"],
        "pages": len(pages),
        "pages_by_locale": dict(sorted(by_locale.items())),
        "screenshots": {status: screenshot_counts.get(status, 0) for status in sorted(VALID_SCREENSHOT_STATUS)},
        "technical_notes": {status: technical_counts.get(status, 0) for status in sorted(VALID_TECHNICAL_STATUS)},
        "doc_gaps": doc_gaps,
    }


def check_documentation(root: Path, config: dict[str, Any], build: bool = False) -> tuple[list[str], list[str], dict[str, Any]]:
    documentation = config.get("documentation")
    if not documentation:
        return [], ["documentation is not configured; structural documentation checks are skipped"], {"configured": False}
    errors: list[str] = []
    warnings: list[str] = []
    docs_root = root / documentation["root"]
    if not docs_root.is_dir():
        errors.append(f"{documentation['root']}: documentation root is missing")
        return errors, warnings, {"configured": True}

    for page in documentation.get("pages", []):
        if not (root / page["path"]).exists():
            errors.append(f"{page['path']}: configured documentation page is missing")

    checked_pages: set[Path] = set()

    def check_page(page: Path) -> None:
        if page in checked_pages or not page.exists():
            return
        checked_pages.add(page)
        text = page.read_text(encoding="utf-8-sig")
        for target in _local_links(text):
            if not (page.parent / target).exists():
                errors.append(f"{page.relative_to(root)}: dead link -> {target}")
        traceability_text = re.sub(r"(?ms)^```.*?^```\s*$", "", text)
        for kind, source in _traceability(traceability_text):
            if not _resolves(root, source):
                errors.append(f"{page.relative_to(root)}: {kind} does not resolve -> {source}")

    for page in _markdown_files(docs_root):
        check_page(page)
    for page in documentation.get("pages", []):
        check_page(root / page["path"])

    rows, screenshot_errors = _screenshot_rows(root, config)
    errors.extend(screenshot_errors)
    screenshots = documentation.get("screenshots", {})
    if screenshots.get("required") and not screenshots.get("index"):
        errors.append("documentation.screenshots.index is required")
    for row in rows:
        page_path = row.get("doc_page", "")
        status = row.get("status", "")
        asset = row.get("asset", "")
        if not page_path or not (docs_root / page_path).exists():
            errors.append(f"screenshot row has missing doc page: {page_path or '(empty)'}")
        if status not in VALID_SCREENSHOT_STATUS:
            errors.append(f"screenshot {asset}: invalid status {status!r}")
        if status == "verified" and row.get("verified_in", "").strip() in {"", "-", "—"}:
            errors.append(f"screenshot {asset}: verified requires verified_in")
        if status not in {"placeholder", "obsolete"}:
            if not asset or not (docs_root / asset).exists():
                errors.append(f"screenshot {asset}: asset is missing for status {status}")
            elif page_path and (docs_root / page_path).exists() and Path(asset).name not in (docs_root / page_path).read_text(encoding="utf-8-sig"):
                warnings.append(f"screenshot {asset}: asset is not referenced by {page_path}")
        ui_source = row.get("ui_source", "").strip()
        if ui_source and ui_source != "—" and not _resolves(root, ui_source):
            errors.append(f"screenshot {asset}: UI source does not resolve -> {ui_source}")

    _, technical_errors = technical_notes(root)
    errors.extend(technical_errors)

    if build and documentation.get("build_command"):
        command = shlex.split(documentation["build_command"])
        completed = subprocess.run(command, cwd=root, check=False)
        if completed.returncode != 0:
            errors.append(f"documentation build failed with exit code {completed.returncode}")
    elif build:
        warnings.append("documentation build requested but build_command is empty")

    return errors, warnings, documentation_metrics(root, config)


def documentation_impact(root: Path, config: dict[str, Any], base: str | None = None) -> dict[str, Any]:
    documentation = config.get("documentation")
    if not documentation:
        return {"configured": False, "changed_files": [], "impacted_pages": [], "unmapped_source": [], "doc_gaps": [], "screenshots": []}
    files_changed = changed_files(root, base)
    docs_root = documentation["root"].rstrip("/") + "/"
    pages = documentation.get("pages", [])
    impacted = []
    gaps = []
    screenshots = []
    screenshot_rows, _ = _screenshot_rows(root, config)
    for page in pages:
        page_path = page["path"]
        patterns = page.get("source_patterns", [])
        direct = page_path in files_changed
        source_changed = any(path_matches_any(path, patterns) for path in files_changed)
        if not direct and not source_changed:
            continue
        exists = (root / page_path).exists()
        impacted.append({"path": page_path, "reason": "direct edit" if direct else "source pattern matched", "exists": exists})
        if not exists:
            gaps.append(page_path)
        for row in screenshot_rows:
            if row.get("doc_page") == page_path.removeprefix(docs_root) and row.get("status") != "obsolete":
                screenshots.append({"asset": row.get("asset"), "status": row.get("status"), "page": page_path})
    mapped_patterns = [pattern for page in pages for pattern in page.get("source_patterns", [])]
    module_patterns = [pattern for module in config["modules"] for pattern in module["paths"]]
    unmapped = []
    for path in files_changed:
        if path.startswith(docs_root) or path.startswith("engineering/") or path.endswith((".md", ".yaml", ".yml")):
            continue
        if path_matches_any(path, module_patterns) and not path_matches_any(path, mapped_patterns):
            unmapped.append(path)
    return {
        "configured": True,
        "base": base,
        "changed_files": files_changed,
        "impacted_pages": impacted,
        "unmapped_source": sorted(unmapped),
        "doc_gaps": sorted(gaps),
        "screenshots": screenshots,
    }


def render_impact_markdown(data: dict[str, Any]) -> str:
    if not data.get("configured"):
        return "# Documentation impact\n\nDocumentation is not configured.\n"
    lines = ["# Documentation impact", "", f"Changed files: {len(data['changed_files'])}", "", "## Impacted pages", ""]
    if not data["impacted_pages"]:
        lines.append("No configured page matched the change set.")
    else:
        lines.extend(f"- `{item['path']}` — {item['reason']}" for item in data["impacted_pages"])
    lines.extend(["", "## Documentation gaps", ""])
    lines.extend(f"- `{path}`" for path in data["doc_gaps"] or ["None identified by path mapping."])
    lines.extend(["", "## Source requiring manual review", ""])
    lines.extend(f"- `{path}`" for path in data["unmapped_source"] or ["None."])
    lines.extend(["", "Path mapping identifies candidates; it does not prove whether behavior is user-visible.", ""])
    return "\n".join(lines)


def render_audit_markdown(root: Path, config: dict[str, Any], base: str | None = None) -> str:
    errors, warnings, metrics = check_documentation(root, config)
    impact = documentation_impact(root, config, base) if base else None
    lines = [
        f"# Documentation audit — {today()}",
        "",
        "## Automated structural findings",
        "",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        f"- Pages: {metrics.get('pages', 0)}",
        f"- Doc gaps on module cards: {metrics.get('doc_gaps', 0)}",
        "",
    ]
    lines.extend(f"- FAIL: {item}" for item in errors)
    lines.extend(f"- WARN: {item}" for item in warnings)
    if impact:
        lines.extend(["", "## Change impact", "", render_impact_markdown(impact).split("\n", 1)[1].strip()])
    lines.extend([
        "",
        "## Required human review",
        "",
        "- Read each impacted page against the current UI or CLI behavior.",
        "- Verify exact labels, defaults, limitations, and error outcomes.",
        "- Check that documented capabilities actually exist.",
        "- Re-capture or verify screenshots against the target build.",
        "- Review declared locales only; do not invent parity for undeclared languages.",
        "- Record semantic corrections in the page and module card, not only in this report.",
        "",
        "## Limitation",
        "",
        "This audit checks structure and traceability. It cannot certify that prose is semantically true.",
        "",
    ])
    return "\n".join(lines)


def plan_docs_initialization(root: Path, config: dict[str, Any]) -> list[tuple[str, str]]:
    documentation = config.get("documentation")
    if not documentation:
        raise ValueError("documentation is not configured")
    docs_root = root / documentation["root"]
    template = files("aeng").joinpath("templates/project/docs")
    actions = []
    for name in ["STYLE.md", "TRACEABILITY.md", "screenshot-index.md"]:
        path = docs_root / name
        actions.append(("preserve" if path.exists() else "create", f"{documentation['root']}/{name}"))
    return actions


def initialize_docs(root: Path, config: dict[str, Any], dry_run: bool = False) -> str:
    actions = plan_docs_initialization(root, config)
    lines = ["Documentation template plan:"]
    lines.extend(f"  {action:8} {path}" for action, path in actions)
    if dry_run:
        return "\n".join(lines)
    documentation = config["documentation"]
    docs_root = root / documentation["root"]
    docs_root.mkdir(parents=True, exist_ok=True)
    template = files("aeng").joinpath("templates/project/docs")
    for name in ["STYLE.md", "TRACEABILITY.md", "screenshot-index.md"]:
        path = docs_root / name
        if not path.exists():
            path.write_text(template.joinpath(name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    return "\n".join(lines) + "\n\nDocumentation templates are ready. Existing files were preserved."
