from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .config import load_config
from .documents import parse_document, parse_table


def _docs(directory: Path):
    for path in sorted(directory.glob("*.md")):
        if not path.name.startswith("_") and path.name != "README.md":
            data, body = parse_document(path)
            yield path, data, body


def collect_report(root: Path) -> dict[str, Any]:
    config = load_config(root)
    plans = []
    for path, data, body in _docs(root / "engineering/plans"):
        _, slices = parse_table(body, "Slices")
        landed = sum(item.get("status") == "landed" for item in slices)
        next_slice = next((item.get("id") for item in slices if item.get("status") != "landed"), "")
        plans.append({
            "id": data.get("id"),
            "module": data.get("module"),
            "status": data.get("status"),
            "updated": str(data.get("updated")),
            "landed": landed,
            "total": len(slices),
            "next_slice": next_slice,
            "blocker": data.get("blocked_by", ""),
        })
    manual = []
    for path, data, _ in _docs(root / "engineering/manual-tests"):
        manual.append({
            "id": data.get("id"),
            "status": data.get("status"),
            "issue": data.get("issue", ""),
            "created": str(data.get("created")),
        })
    decisions = [data.get("id") for _, data, _ in _docs(root / "engineering/decisions")]
    return {
        "generated": date.today().isoformat(),
        "project": config["project"]["name"],
        "plans": plans,
        "plan_status_counts": dict(Counter(item["status"] for item in plans)),
        "manual_status_counts": dict(Counter(item["status"] for item in manual)),
        "open_manual": [item for item in manual if item["status"] in {"pending", "failed", "blocked"}],
        "decisions": len(decisions),
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# Engineering report - {data['generated']}",
        "",
        f"Project: **{data['project']}**",
        "",
        "## Plans",
        "",
        "| Plan | Module | Status | Progress | Next slice | Blocker |",
        "|---|---|---|---|---|---|",
    ]
    for item in data["plans"]:
        if item["status"] in {"superseded", "abandoned"}:
            continue
        lines.append(
            f"| {item['id']} | {item['module']} | {item['status']} | {item['landed']}/{item['total']} | "
            f"{item['next_slice'] or '-'} | {item['blocker'] or '-'} |"
        )
    lines.extend(["", "## Verification backlog", ""])
    if not data["open_manual"]:
        lines.append("No open manual checks.")
    else:
        lines.extend(["| Check | Status | Issue | Created |", "|---|---|---|---|"])
        for item in data["open_manual"]:
            lines.append(f"| {item['id']} | {item['status']} | {item['issue']} | {item['created']} |")
    lines.extend(["", f"Durable decisions: {data['decisions']}.", ""])
    return "\n".join(lines)


def render_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
