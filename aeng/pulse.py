from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .docs import documentation_metrics
from .documents import parse_document, parse_table, today
from .report import collect_report


def _git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def _module_snapshot(root: Path) -> list[dict[str, Any]]:
    modules = []
    for path in sorted((root / "engineering/modules").glob("*.md")):
        if path.name.startswith("_"):
            continue
        data, body = parse_document(path)
        _, rows = parse_table(body, "Features")
        maturity = {}
        for row in rows:
            value = row.get("maturity", "unknown")
            maturity[value] = maturity.get(value, 0) + 1
        modules.append({
            "id": data.get("id", path.stem),
            "name": data.get("name", path.stem),
            "updated": str(data.get("updated", "")),
            "maturity": maturity,
            "doc_gaps": sum("doc gap" in row.get("docs", "").lower() for row in rows),
        })
    return modules


def _plan_changes(current: list[dict[str, Any]], previous: dict[str, Any] | None) -> dict[str, list[Any]]:
    if previous is None:
        return {"new_plans": [], "retired_plans": [], "changed_plans": []}
    old = {item["id"]: item for item in previous.get("plans", [])}
    new = {item["id"]: item for item in current}
    changed = []
    for plan_id, plan in new.items():
        if plan_id not in old:
            continue
        before = old[plan_id]
        fields = ["status", "updated", "landed", "total"]
        differences = {field: {"before": before.get(field), "after": plan.get(field)} for field in fields if before.get(field) != plan.get(field)}
        if differences:
            changed.append({"id": plan_id, "changes": differences})
    return {
        "new_plans": sorted(set(new) - set(old)),
        "retired_plans": sorted(set(old) - set(new)),
        "changed_plans": changed,
    }


def collect_pulse(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    pulse_dir = root / "engineering/pulse"
    latest_path = pulse_dir / "latest.json"
    previous = None
    if latest_path.exists():
        previous = json.loads(latest_path.read_text(encoding="utf-8-sig"))
    report = collect_report(root)
    documentation = documentation_metrics(root, config)
    changes = _plan_changes(report["plans"], previous)
    return {
        "version": 1,
        "generated": today(),
        "previous": (previous or {}).get("generated"),
        "head": _git_value(root, "rev-parse", "--short", "HEAD"),
        "branch": _git_value(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "project": config["project"]["name"],
        "plans": report["plans"],
        "plan_status_counts": report["plan_status_counts"],
        "manual_status_counts": report["manual_status_counts"],
        "open_manual": report["open_manual"],
        "decisions": report["decisions"],
        "documentation": documentation,
        "modules": _module_snapshot(root),
        "changes": changes,
        "baseline": previous is None,
        "limits": [
            "Plan movement is inferred from plan metadata and slice status, not code completeness.",
            "Documentation metrics are structural; semantic truth requires human review.",
            "Screenshots require build-specific human verification.",
            "A CI artifact is not a persistent baseline until it is committed or otherwise retained.",
        ],
    }


def render_pulse_markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# Engineering pulse - {data['generated']}",
        "",
        f"- Project: **{data['project']}**",
        f"- Branch: `{data['branch']}` @ `{data['head']}`",
        f"- Previous baseline: {data['previous'] or 'none (baseline run)'}",
        "",
        "## Plan movement",
        "",
    ]
    changes = data["changes"]
    lines.append(f"- New: {len(changes['new_plans'])}")
    lines.append(f"- Retired: {len(changes['retired_plans'])}")
    lines.append(f"- Changed: {len(changes['changed_plans'])}")
    for plan_id in changes["new_plans"]:
        lines.append(f"- New plan: `{plan_id}`")
    for plan_id in changes["retired_plans"]:
        lines.append(f"- Retired plan: `{plan_id}`")
    for item in changes["changed_plans"]:
        lines.append(f"- Changed plan: `{item['id']}` — {', '.join(item['changes'])}")
    lines.extend(["", "## Active work", "", "| Plan | Status | Progress | Next slice | Blocker |", "|---|---|---|---|---|"])
    for plan in data["plans"]:
        if plan["status"] in {"superseded", "abandoned"}:
            continue
        lines.append(f"| {plan['id']} | {plan['status']} | {plan['landed']}/{plan['total']} | {plan['next_slice'] or '-'} | {plan['blocker'] or '-'} |")
    documentation = data["documentation"]
    lines.extend([
        "",
        "## Documentation",
        "",
        f"- Configured: {documentation.get('configured', False)}",
        f"- Markdown pages: {documentation.get('pages', 0)}",
        f"- Module-card doc gaps: {documentation.get('doc_gaps', 0)}",
        f"- Technical notes: {documentation.get('technical_notes', {})}",
        f"- Screenshots: {documentation.get('screenshots', {})}",
        "",
        "## Verification backlog",
        "",
        f"- Open manual checks: {len(data['open_manual'])}",
        f"- Durable decisions: {data['decisions']}",
        "",
        "## Limits",
        "",
    ])
    lines.extend(f"- {item}" for item in data["limits"])
    lines.append("")
    return "\n".join(lines)


def write_pulse(root: Path, config: dict[str, Any], output_dir: str = "engineering/pulse") -> tuple[Path, Path, dict[str, Any]]:
    data = collect_pulse(root, config)
    directory = root / output_dir
    directory.mkdir(parents=True, exist_ok=True)
    latest = directory / "latest.json"
    report = directory / f"progression-{data['generated']}.md"
    latest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    report.write_text(render_pulse_markdown(data), encoding="utf-8", newline="\n")
    return latest, report, data
