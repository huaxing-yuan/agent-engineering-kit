from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

from .config import path_matches_any


def changed_files(root: Path, base: str | None = None) -> list[str]:
    def run(args: list[str]) -> list[str]:
        completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            raise ValueError(completed.stderr.strip() or "Git change detection failed")
        return [line for line in completed.stdout.splitlines() if line]

    if base:
        return sorted(set(run(["diff", "--name-only", base]) + run(["ls-files", "--others", "--exclude-standard"])))
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=root, capture_output=True, check=False)
    tracked = run(["diff", "--name-only", "HEAD"]) if head.returncode == 0 else []
    untracked = run(["ls-files", "--others", "--exclude-standard"])
    return sorted(set(tracked + untracked))


def select_tests(root: Path, config: dict[str, Any], base: str | None = None) -> dict[str, Any]:
    files = changed_files(root, base)
    broad = config["test"].get("broad_change", {})
    broad_paths = broad.get("paths", [])
    broad_hit = next((path for path in files if path_matches_any(path, broad_paths)), "")
    areas = []
    for area, patterns in config["test"].get("areas", {}).items():
        if any(path_matches_any(path, patterns) for path in files):
            areas.append(area)
    modules_touched = len(areas)
    source_files = [path for path in files if not path.endswith((".md", ".yaml", ".yml", ".json", ".lock"))]
    reason = ""
    command = ""
    fallback = False
    if broad_hit:
        reason = f"broad-change path matched: {broad_hit}"
        command = config["test"].get("full_command") or config["test"].get("fast_command") or config["test"].get("default_command", "")
        fallback = True
    elif len(source_files) > broad.get("max_files", 30):
        reason = f"{len(source_files)} changed source files exceed the selection budget"
        command = config["test"].get("fast_command") or config["test"].get("default_command", "")
        fallback = True
    elif modules_touched >= broad.get("max_modules", 4):
        reason = f"{modules_touched} modules touched; selection is too broad"
        command = config["test"].get("fast_command") or config["test"].get("default_command", "")
        fallback = True
    elif areas:
        area_commands = config["test"].get("area_commands", {})
        commands = [area_commands[area] for area in areas if area_commands.get(area)]
        command = " && ".join(commands) if commands else config["test"].get("default_command", "")
        reason = "mapped areas: " + ", ".join(areas)
    elif source_files:
        reason = "changed source files did not match a configured area"
        command = config["test"].get("default_command", "")
        fallback = True
    else:
        reason = "no production source changes detected"
    return {
        "files": files,
        "areas": areas,
        "reason": reason,
        "command": command,
        "fallback": fallback,
        "executed": False,
    }


def run_selection(root: Path, selection: dict[str, Any]) -> int:
    command = selection.get("command", "")
    if not command:
        print("No test command configured. Update .agent-engineering.yaml.")
        return 2
    for part in command.split("&&"):
        args = shlex.split(part.strip())
        if not args:
            continue
        print("+ " + " ".join(args), flush=True)
        completed = subprocess.run(args, cwd=root, check=False)
        if completed.returncode != 0:
            return completed.returncode
    selection["executed"] = True
    return 0
