from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any

from .documents import render_template, today, write_document
from .indexes import update_indexes


def _destination_relative(relative: str) -> str:
    prefix = "agent-instructions/agent-engineering/"
    if relative.startswith(prefix):
        return ".github/instructions/agent-engineering/" + relative.removeprefix(prefix)
    return relative


def _template_root():
    return files("aeng").joinpath("templates/project")


def _template_files(base):
    for item in sorted(base.iterdir(), key=lambda path: path.name):
        if item.is_dir():
            yield from _template_files(item)
        elif item.is_file():
            yield item


def _values(config: dict[str, Any]) -> dict[str, str]:
    project = config["project"]
    test = config["test"]
    commands = config.get("commands", {})
    rows = [
        f"| Affected tests | `{test.get('default_command', '')}` |",
        f"| Fast gate | `{test.get('fast_command', '')}` |",
        f"| Full gate | `{test.get('full_command', '')}` |",
        f"| Build | `{commands.get('build', '')}` |",
        f"| Lint | `{commands.get('lint', '')}` |",
        "| Governance | `aeng check` |",
    ]
    existing = config.get("existing", {})
    instruction_files = existing.get("instruction_files", [])
    return {
        "PROJECT_NAME": str(project["name"]),
        "LANGUAGES": ", ".join(project["languages"]),
        "SOURCE_ROOTS": ", ".join(f"`{item}`" for item in project.get("source_roots", [])),
        "DOCS_ROOT": str(project.get("docs_root", "docs")),
        "COMMAND_TABLE": "\n".join(rows),
        "UNIT_COMMAND": str(test.get("default_command", "")),
        "INTEGRATION_COMMAND": str(test.get("fast_command", "")),
        "HEADLESS_COMMAND": str(test.get("area_commands", {}).get("ui", "")),
        "E2E_COMMAND": "",
        "LIVE_COMMAND": "",
        "EXISTING_INSTRUCTIONS": ", ".join(f"`{item}`" for item in instruction_files) or "None detected",
    }


def _integration_block(config: dict[str, Any]) -> str:
    return f"""# Agent Engineering integration

The repository uses `agent-engineering-kit` for project memory and verification.

- Read `engineering/README.md` before engineering work.
- Scan `engineering/decisions/README.md` before proposing a design.
- Use `engineering/plans/` for multi-slice or cross-layer work.
- Run `aeng check` before declaring a task complete.
- Preserve all existing project instructions; surface conflicts instead of replacing them.

Project: {config['project']['name']}
"""


def plan_initialization(root: Path, config: dict[str, Any], adopt_existing: bool = False) -> tuple[list[tuple[str, str, str]], list[str]]:
    root = root.resolve()
    actions: list[tuple[str, str, str]] = []
    notes: list[str] = []
    engineering = root / "engineering"
    existing_engineering = engineering.exists() and any(path.is_file() for path in engineering.rglob("*"))
    if existing_engineering and not adopt_existing:
        raise ValueError(
            "engineering/ already exists and is not empty. Re-run with --adopt-existing to add only missing files; "
            "existing files will not be overwritten."
        )

    for name in ["AGENTS.md", "CLAUDE.md"]:
        path = root / name
        if path.exists():
            actions.append(("preserve", name, "Existing file kept unchanged"))
        else:
            actions.append(("create", name, "Root agent contract" if name == "AGENTS.md" else "Thin pointer to AGENTS.md"))

    template = _template_root()
    for item in _template_files(template):
        relative = _destination_relative(item.relative_to(template).as_posix())
        if relative in {"AGENTS.md", "CLAUDE.md"} or relative.startswith("docs/"):
            continue
        path = root / relative
        if path.exists():
            actions.append(("preserve", relative, "Existing file kept unchanged"))
        else:
            actions.append(("create", relative, "Engineering template or namespaced area instruction"))

    if (root / "AGENTS.md").exists() or (root / "CLAUDE.md").exists():
        actions.append(("create", ".agent-engineering/integration-block.md", "Review and merge explicitly; never auto-appended"))

    for module in config["modules"]:
        relative = f"engineering/modules/{module['id']}.md"
        path = root / relative
        if path.exists():
            actions.append(("preserve", relative, "Existing module card kept unchanged"))
        else:
            actions.append(("create", relative, "Module card generated from configuration"))

    if existing_engineering:
        notes.append("Existing engineering files were preserved. Review legacy frontmatter and indexes before relying on aeng check.")
    else:
        notes.append("Clean initialization will generate PROJECT.md and all lifecycle indexes.")
    instructions = config.get("existing", {}).get("instruction_files", [])
    if instructions:
        notes.append("Existing instruction files remain authoritative for their scope: " + ", ".join(instructions))
    if not config["test"].get("default_command"):
        notes.append("No test command was discovered. Set test.default_command before using test selection.")
    if config.get("documentation"):
        notes.append("Documentation templates are explicit: run 'aeng docs init' after reviewing the documentation root.")
    return actions, notes


def initialize_project(root: Path, config: dict[str, Any], adopt_existing: bool = False, dry_run: bool = False) -> str:
    actions, notes = plan_initialization(root, config, adopt_existing)
    lines = ["Initialization plan:"]
    for action, relative, reason in actions:
        lines.append(f"  {action:8} {relative} - {reason}")
    lines.append("")
    lines.extend(f"Note: {note}" for note in notes)
    if dry_run:
        return "\n".join(lines)

    root = root.resolve()
    had_existing_agent_contract = (root / "AGENTS.md").exists() or (root / "CLAUDE.md").exists()
    had_existing_engineering = (root / "engineering").exists() and any(path.is_file() for path in (root / "engineering").rglob("*"))
    values = _values(config)
    template = _template_root()
    for item in _template_files(template):
        relative = _destination_relative(item.relative_to(template).as_posix())
        if relative in {"AGENTS.md", "CLAUDE.md"} or relative.startswith("docs/"):
            continue
        destination = root / relative
        if destination.exists():
            continue
        text = render_template(item.read_text(encoding="utf-8"), values)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8", newline="\n")

    for name in ["AGENTS.md", "CLAUDE.md"]:
        destination = root / name
        if destination.exists():
            continue
        text = render_template(template.joinpath(name).read_text(encoding="utf-8"), values)
        destination.write_text(text, encoding="utf-8", newline="\n")

    integration = root / ".agent-engineering/integration-block.md"
    if had_existing_agent_contract:
        integration.parent.mkdir(parents=True, exist_ok=True)
        integration.write_text(_integration_block(config), encoding="utf-8", newline="\n")

    module_template = template.joinpath("engineering/modules/_TEMPLATE.md").read_text(encoding="utf-8")
    for module in config["modules"]:
        destination = root / "engineering/modules" / f"{module['id']}.md"
        if destination.exists():
            continue
        body = module_template.split("---", 2)[-1].lstrip()
        body = body.replace("# Module Name", f"# {module['name']}")
        body = body.replace("| Example capability | brainstorm | no | no | Evidence or review date |", "| Define a user-visible capability | brainstorm | no | no | Add evidence and review date |")
        write_document(destination, {
            "id": module["id"],
            "name": module["name"],
            "responsibility": module.get("responsibility", "Review and describe this module."),
            "updated": today(),
        }, body)

    report = root / ".agent-engineering/adoption-report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report_lines = ["# Adoption report", "", f"Generated: {today()}", "", "## Actions", ""]
    report_lines.extend(f"- **{action}** `{relative}` - {reason}" for action, relative, reason in actions)
    report_lines.extend(["", "## Notes", ""])
    report_lines.extend(f"- {note}" for note in notes)
    if (root / "AGENTS.md").exists() and had_existing_agent_contract:
        report_lines.extend([
            "",
            "## Required review",
            "",
            "An existing `AGENTS.md` was preserved. Review `.agent-engineering/integration-block.md` and merge it explicitly if appropriate.",
        ])
    if (root / "CLAUDE.md").exists():
        report_lines.append("- Review `CLAUDE.md`; it should point to `AGENTS.md` rather than duplicate the contract.")
    report.write_text("\n".join(report_lines).rstrip() + "\n", encoding="utf-8", newline="\n")

    if not had_existing_engineering:
        update_indexes(root)
    return "\n".join(lines) + "\n\nInitialization complete. Review .agent-engineering/adoption-report.md, then run 'aeng check'."
