from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .config import load_config
from .documents import parse_document, parse_table
from .indexes import generated_documents

VALID_PLAN_TYPES = {"plan", "investigation", "design", "migration"}
VALID_PLAN_STATUS = {"draft", "in-progress", "dev-finished", "blocked", "superseded", "abandoned"}
VALID_DECISIONS = {"accepted", "rejected", "deferred", "superseded"}
VALID_MANUAL_STATUS = {"pending", "verified", "failed", "blocked", "obsolete"}
VALID_SLICE_STATUS = {"planned", "in-progress", "landed", "blocked"}


def _date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _markdown_links(text: str):
    text = re.sub(r"(?ms)^```.*?^```\s*$", "", text)
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0].split("?", 1)[0].strip()
        if target and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) and "{{" not in target:
            yield target


def validate(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        config = load_config(root)
    except (ValueError, yaml.YAMLError) as exc:
        return [str(exc)], warnings
    module_ids = {module["id"] for module in config["modules"]}
    stale_days = config.get("verification", {}).get("stale_days", 30)
    now = date.today()
    engineering = root / "engineering"
    if not engineering.is_dir():
        return ["engineering/ is missing. Run 'aeng init'."], warnings

    plan_dir = engineering / "plans"
    for path in sorted(plan_dir.glob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        try:
            data, body = parse_document(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
            continue
        required = {"id", "module", "type", "status", "updated", "manual_required", "docs_impact", "decisions_captured"}
        missing = sorted(required - set(data))
        if missing:
            errors.append(f"{path.name}: missing frontmatter keys: {', '.join(missing)}")
        if data.get("id") != path.stem:
            errors.append(f"{path.name}: id must match the filename")
        if data.get("module") not in module_ids:
            errors.append(f"{path.name}: unknown module {data.get('module')!r}")
        if data.get("type") not in VALID_PLAN_TYPES:
            errors.append(f"{path.name}: invalid type {data.get('type')!r}")
        status = data.get("status")
        if status == "done":
            errors.append(f"{path.name}: done plans must be retired, not stored")
        elif status not in VALID_PLAN_STATUS:
            errors.append(f"{path.name}: invalid status {status!r}")
        updated = _date(data.get("updated"))
        if not updated:
            errors.append(f"{path.name}: updated must be YYYY-MM-DD")
        elif status in {"in-progress", "blocked"} and (now - updated).days > stale_days:
            warnings.append(f"{path.name}: inactive for {(now - updated).days} days")
        if len(body.splitlines()) > 220:
            warnings.append(f"{path.name}: plan body exceeds 220 lines; move long-form design to technical/")
        if data.get("docs_impact") not in {"pending", "complete", "not-required"}:
            errors.append(f"{path.name}: docs_impact must be pending, complete, or not-required")
        if status == "blocked" and not data.get("blocked_by"):
            errors.append(f"{path.name}: blocked plan requires blocked_by")
        if status == "superseded" and not data.get("superseded_by"):
            errors.append(f"{path.name}: superseded plan requires superseded_by")
        _, rows = parse_table(body, "Slices")
        if not rows:
            errors.append(f"{path.name}: Slices table is missing or empty")
        ids = [row.get("id") for row in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"{path.name}: duplicate slice id")
        for row in rows:
            if row.get("status") not in VALID_SLICE_STATUS:
                errors.append(f"{path.name}: slice {row.get('id')} has invalid status")
            if row.get("status") == "landed" and row.get("evidence", "").strip() in {"", "—", "-"}:
                errors.append(f"{path.name}: landed slice {row.get('id')} requires evidence")
        if status == "dev-finished":
            if not rows or any(row.get("status") != "landed" for row in rows):
                errors.append(f"{path.name}: dev-finished requires every slice to be landed")
            if not data.get("manual_required"):
                errors.append(f"{path.name}: dev-finished requires manual_required: true")
            pending = []
            for manual_path in (engineering / "manual-tests").glob("*.md"):
                if manual_path.name.startswith("_") or manual_path.name == "README.md":
                    continue
                try:
                    manual, _ = parse_document(manual_path)
                except (ValueError, yaml.YAMLError):
                    continue
                source = str(manual.get("source", "")).replace("\\", "/")
                if manual.get("status") == "pending" and (source == path.stem or source.endswith(f"{path.stem}.md")):
                    pending.append(manual_path)
            if not pending:
                errors.append(f"{path.name}: dev-finished requires a pending manual test sourced from this plan")

    for path in sorted((engineering / "decisions").glob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        try:
            data, _ = parse_document(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
            continue
        if not re.fullmatch(r"dec-\d{4}-\d{2}-\d{2}-[a-z0-9-]+", path.stem):
            errors.append(f"{path.name}: decision filename must be dec-YYYY-MM-DD-kebab-case-title.md")
        if data.get("id") != path.stem:
            errors.append(f"{path.name}: id must match the filename")
        if data.get("module") not in module_ids:
            errors.append(f"{path.name}: unknown module {data.get('module')!r}")
        if data.get("decision") not in VALID_DECISIONS:
            errors.append(f"{path.name}: invalid decision {data.get('decision')!r}")
        if not _date(data.get("date")):
            errors.append(f"{path.name}: date must be YYYY-MM-DD")
        if data.get("decision") == "superseded" and not data.get("superseded_by"):
            errors.append(f"{path.name}: superseded decision requires superseded_by")
        guards = data.get("enforced_by", [])
        if isinstance(guards, str):
            guards = [guards]
        for guard in guards:
            if not (root / str(guard)).exists():
                errors.append(f"{path.name}: enforced_by path does not exist: {guard}")

    issue_required = config.get("github", {}).get("issue_required", True)
    for path in sorted((engineering / "manual-tests").glob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        try:
            data, _ = parse_document(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
            continue
        if data.get("id") != path.stem:
            errors.append(f"{path.name}: id must match the filename")
        if data.get("module") not in module_ids:
            errors.append(f"{path.name}: unknown module {data.get('module')!r}")
        status = data.get("status")
        if status not in VALID_MANUAL_STATUS:
            errors.append(f"{path.name}: invalid status {status!r}")
        for key in ["created", "updated"]:
            if not _date(data.get(key)):
                errors.append(f"{path.name}: {key} must be YYYY-MM-DD")
        if status == "verified" and not data.get("verified_in"):
            errors.append(f"{path.name}: verified requires verified_in")
        if status != "obsolete" and issue_required and not data.get("issue"):
            errors.append(f"{path.name}: issue is required (set github.issue_required false for a no-issue tracker)")
        created = _date(data.get("created"))
        if status == "pending" and created and (now - created).days > stale_days:
            warnings.append(f"{path.name}: pending for {(now - created).days} days")

    matrix_path = engineering / "verification/test-matrix.yaml"
    if not matrix_path.exists():
        errors.append("engineering/verification/test-matrix.yaml is missing")
    else:
        try:
            matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
            if not isinstance(matrix.get("layers"), list) or not matrix["layers"]:
                errors.append("test-matrix.yaml must define a non-empty layers list")
        except yaml.YAMLError as exc:
            errors.append(f"test-matrix.yaml: {exc}")

    known_path = engineering / "verification/known-failures.yaml"
    if not known_path.exists():
        errors.append("engineering/verification/known-failures.yaml is missing")
    else:
        try:
            known = yaml.safe_load(known_path.read_text(encoding="utf-8")) or {}
            for item in known.get("failures", []):
                required = {"test_id", "owner", "issue", "reason", "expires"}
                if required - set(item):
                    errors.append(f"known failure missing keys: {sorted(required - set(item))}")
                    continue
                expiry = _date(item.get("expires"))
                if not expiry:
                    errors.append(f"known failure {item.get('test_id')}: expires must be YYYY-MM-DD")
                elif expiry < now:
                    errors.append(f"known failure {item.get('test_id')}: expired on {expiry}")
        except yaml.YAMLError as exc:
            errors.append(f"known-failures.yaml: {exc}")

    try:
        generated = generated_documents(root, config)
        for relative, expected in generated.items():
            path = root / relative
            if not path.exists():
                errors.append(f"{relative}: missing generated artifact")
            elif path.read_text(encoding="utf-8").rstrip() != expected.rstrip():
                errors.append(f"{relative}: generated content is stale; run 'aeng index'")
    except (ValueError, yaml.YAMLError, OSError) as exc:
        errors.append(f"Could not validate generated indexes: {exc}")

    for path in sorted(engineering.rglob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        for target in _markdown_links(text):
            if not (path.parent / target).exists():
                errors.append(f"{path.relative_to(root)}: dead link -> {target}")

    if not (root / "AGENTS.md").exists():
        errors.append("AGENTS.md is missing")
    else:
        root_lines = len((root / "AGENTS.md").read_text(encoding="utf-8").splitlines())
        if root_lines > 180:
            warnings.append(f"AGENTS.md has {root_lines} lines; route detail into area instructions")
    claude = root / "CLAUDE.md"
    if claude.exists() and "AGENTS.md" not in claude.read_text(encoding="utf-8"):
        warnings.append("CLAUDE.md should point to AGENTS.md instead of duplicating rules")
    return errors, warnings
