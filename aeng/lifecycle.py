from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from .config import load_config
from .documents import (
    append_table_row,
    parse_document,
    parse_table,
    set_table_row,
    slugify,
    today,
    write_document,
)
from .indexes import update_indexes

VALID_PLAN_STATUS = {"draft", "in-progress", "dev-finished", "blocked", "done", "superseded", "abandoned"}
VALID_SLICE_STATUS = {"planned", "in-progress", "landed", "blocked"}


def _plan_path(root: Path, plan_id: str) -> Path:
    path = root / "engineering/plans" / f"{plan_id}.md"
    if not path.exists():
        raise ValueError(f"Plan not found: {plan_id}")
    return path


def create_plan(root: Path, title: str, module: str, plan_type: str, outcome: str, non_goals: str) -> Path:
    plan_id = slugify(title)
    path = root / "engineering/plans" / f"{plan_id}.md"
    if path.exists():
        raise ValueError(f"Plan already exists: {plan_id}")
    body = f"""# {title}

## Outcome

{outcome or 'Define one observable result.'}

## Non-goals

{non_goals or 'State what this plan deliberately does not change.'}

## Current evidence

Add file references, measurements, and reproduction steps.

## Related decisions

- Scan `engineering/decisions/README.md` and link relevant rulings.

## Slices

| ID | Scope | Verification | Status | Evidence |
|---|---|---|---|---|
| S1 | Define the first independently verifiable slice | Named tests or checks | planned | — |

## Gates

- G1: Define an objective exit condition.

## Documentation impact

`pending | complete | not-required`

Explain the decision in this section.

## Manual verification

Set `manual_required` in frontmatter and link entries in `manual-tests/` when needed.

## Risks and rollback

- Risk:
- Rollback:

## Landing log

- {today()} — Plan created.
"""
    write_document(path, {
        "id": plan_id,
        "module": module,
        "type": plan_type,
        "status": "draft",
        "owner": "maintainer",
        "updated": today(),
        "manual_required": False,
        "docs_impact": "pending",
        "decisions_captured": False,
        "blocked_by": "",
        "superseded_by": "",
    }, body)
    update_indexes(root)
    return path


def add_slice(root: Path, plan_id: str, slice_id: str, scope: str, verification: str) -> None:
    path = _plan_path(root, plan_id)
    data, body = parse_document(path)
    _, rows = parse_table(body, "Slices")
    if any(row.get("id") == slice_id for row in rows):
        raise ValueError(f"Slice already exists: {slice_id}")
    body = append_table_row(body, "Slices", {
        "id": slice_id,
        "scope": scope,
        "verification": verification,
        "status": "planned",
        "evidence": "—",
    })
    data["updated"] = today()
    write_document(path, data, body)
    update_indexes(root)


def set_slice(root: Path, plan_id: str, slice_id: str, status: str, evidence: str = "") -> None:
    if status not in VALID_SLICE_STATUS:
        raise ValueError(f"Invalid slice status: {status}")
    path = _plan_path(root, plan_id)
    data, body = parse_document(path)
    updates = {"status": status}
    if evidence:
        updates["evidence"] = evidence
    if status == "landed" and not evidence:
        raise ValueError("A landed slice requires --evidence")
    body = set_table_row(body, "Slices", slice_id, updates)
    data["updated"] = today()
    if data.get("status") == "draft" and status == "in-progress":
        data["status"] = "in-progress"
    write_document(path, data, body)
    update_indexes(root)


def _related_manual(root: Path, plan_id: str) -> list[tuple[Path, dict[str, Any]]]:
    result = []
    for path in sorted((root / "engineering/manual-tests").glob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue
        data, _ = parse_document(path)
        source = str(data.get("source", "")).replace("\\", "/")
        if source.endswith(f"{plan_id}.md") or source == plan_id:
            result.append((path, data))
    return result


def set_plan_status(root: Path, plan_id: str, status: str, blocker: str = "", successor: str = "") -> None:
    if status not in VALID_PLAN_STATUS - {"done"}:
        raise ValueError(f"Invalid plan status: {status}")
    path = _plan_path(root, plan_id)
    data, body = parse_document(path)
    if status == "dev-finished":
        _, slices = parse_table(body, "Slices")
        if not slices or any(row.get("status") != "landed" for row in slices):
            raise ValueError("dev-finished requires every slice to be landed")
        if not data.get("manual_required"):
            raise ValueError("dev-finished requires manual_required: true")
        pending = [item for item in _related_manual(root, plan_id) if item[1].get("status") == "pending"]
        if not pending:
            raise ValueError("dev-finished requires at least one pending manual test sourced from this plan")
    if status == "blocked" and not blocker:
        raise ValueError("blocked requires --blocker with an exit condition")
    if status == "superseded" and not successor:
        raise ValueError("superseded requires --successor")
    data["status"] = status
    data["updated"] = today()
    if status == "blocked":
        data["blocked_by"] = blocker
    elif status != "blocked":
        data["blocked_by"] = ""
    if status == "superseded":
        data["superseded_by"] = successor
    write_document(path, data, body)
    update_indexes(root)


def retire_plan(root: Path, plan_id: str) -> None:
    path = _plan_path(root, plan_id)
    data, body = parse_document(path)
    _, rows = parse_table(body, "Slices")
    if not rows or any(row.get("status") != "landed" for row in rows):
        raise ValueError("All slices must be landed before retirement")
    if data.get("docs_impact") not in {"complete", "not-required"}:
        raise ValueError("Documentation impact must be complete or not-required")
    if not data.get("decisions_captured"):
        raise ValueError("Set decisions_captured: true after durable rulings are captured")
    if data.get("manual_required"):
        related = _related_manual(root, plan_id)
        if not related or any(item[1].get("status") not in {"verified", "obsolete"} for item in related):
            raise ValueError("All required manual tests must be verified or obsolete")
    path.unlink()
    update_indexes(root)


def create_decision(
    root: Path,
    title: str,
    module: str,
    decision: str,
    context: str,
    ruling: str,
    consequences: str,
    reopen_if: str,
    enforced_by: list[str] | None = None,
) -> Path:
    if decision not in {"accepted", "rejected", "deferred", "superseded"}:
        raise ValueError(f"Invalid decision value: {decision}")
    decision_id = f"dec-{today()}-{slugify(title)}"
    path = root / "engineering/decisions" / f"{decision_id}.md"
    if path.exists():
        raise ValueError(f"Decision already exists: {decision_id}")
    body = f"""# {title}

## Context

{context}

## Decision

{ruling}

## Consequences

{consequences}

## Reopen only if

{reopen_if or 'New evidence invalidates a stated constraint.'}
"""
    write_document(path, {
        "id": decision_id,
        "module": module,
        "decision": decision,
        "date": today(),
        "related": "",
        "enforced_by": enforced_by or [],
        "superseded_by": "",
    }, body)
    update_indexes(root)
    return path


def _create_github_issue(root: Path, title: str, body: str, label: str) -> str:
    completed = subprocess.run(
        ["gh", "issue", "create", "--title", title, "--body", body, "--label", label],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(f"GitHub issue creation failed: {completed.stderr.strip()}")
    match = re.search(r"/issues/(\d+)", completed.stdout)
    if not match:
        raise ValueError("GitHub issue was created but its number could not be read; inspect GitHub and update the entry manually")
    return match.group(1)


def create_manual_test(root: Path, title: str, module: str, source: str, issue: str = "", create_issue: bool = False) -> Path:
    manual_id = slugify(title)
    path = root / "engineering/manual-tests" / f"{manual_id}.md"
    if path.exists():
        raise ValueError(f"Manual test already exists: {manual_id}")
    if create_issue:
        config = load_config(root)
        issue = _create_github_issue(
            root,
            title,
            f"Manual verification for `{source or manual_id}`.\n\nChecklist: `engineering/manual-tests/{manual_id}.md`",
            config.get("github", {}).get("manual_test_label", "manual testing"),
        )
    body = f"""# {title}

## Why manual

Describe what current automated layers cannot prove.

## Prerequisites

Build, account, data, device, or environment.

## Steps

1. Perform the exact action.
2. Observe the result.

## Expected results

- State the expected result precisely.

## Evidence

Add screenshots, logs, or explicit human confirmation.

## Related

- Source: `{source or manual_id}`
"""
    write_document(path, {
        "id": manual_id,
        "module": module,
        "status": "pending",
        "created": today(),
        "updated": today(),
        "source": source,
        "verified_in": "",
        "issue": issue,
        "evidence": [],
    }, body)
    update_indexes(root)
    return path


def close_manual_test(root: Path, manual_id: str, verified_in: str, confirmed_by: str, evidence: str, close_issue: bool = False) -> None:
    path = root / "engineering/manual-tests" / f"{manual_id}.md"
    if not path.exists():
        raise ValueError(f"Manual test not found: {manual_id}")
    if not verified_in or not confirmed_by:
        raise ValueError("--verified-in and --confirmed-by are required")
    data, body = parse_document(path)
    data["status"] = "verified"
    data["updated"] = today()
    data["verified_in"] = verified_in
    data["confirmed_by"] = confirmed_by
    data["evidence"] = list(data.get("evidence", [])) + ([evidence] if evidence else [])
    write_document(path, data, body)
    if close_issue and data.get("issue"):
        completed = subprocess.run(
            ["gh", "issue", "close", str(data["issue"]), "--comment", f"Verified in {verified_in} by {confirmed_by}."],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ValueError(f"Entry verified, but GitHub issue closure failed: {completed.stderr.strip()}")
    update_indexes(root)
