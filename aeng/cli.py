from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .config import CONFIG_NAME, discover, dump_config, load_config, validate_config
from .documents import today
from .indexes import update_indexes
from .initializer import initialize_project
from .lifecycle import (
    add_slice,
    close_manual_test,
    create_decision,
    create_manual_test,
    create_plan,
    retire_plan,
    set_plan_status,
    set_slice,
)
from .report import collect_report, render_json, render_markdown
from .test_selector import run_selection, select_tests
from .validator import validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aeng", description="Repository-native memory and verification for coding agents")
    parser.add_argument("--version", action="version", version=f"aeng {__version__}")
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    sub = parser.add_subparsers(dest="command", required=True)

    discover_parser = sub.add_parser("discover", help="Inspect a project and draft .agent-engineering.yaml")
    discover_parser.add_argument("--output", default=CONFIG_NAME)
    discover_parser.add_argument("--stdout", action="store_true")
    discover_parser.add_argument("--force", action="store_true")

    init_parser = sub.add_parser("init", help="Safely install contracts and engineering artifacts")
    init_parser.add_argument("--config", default=CONFIG_NAME)
    init_parser.add_argument("--adopt-existing", action="store_true")
    init_parser.add_argument("--dry-run", action="store_true")

    sub.add_parser("check", help="Validate governance artifacts and generated indexes")
    sub.add_parser("index", help="Regenerate all indexes and PROJECT.md")

    report_parser = sub.add_parser("report", help="Print a derived progress report")
    report_parser.add_argument("--json", action="store_true")
    report_parser.add_argument("--output")

    plan = sub.add_parser("plan", help="Manage active plans")
    plan_sub = plan.add_subparsers(dest="plan_command", required=True)
    new = plan_sub.add_parser("new")
    new.add_argument("title")
    new.add_argument("--module", required=True)
    new.add_argument("--type", default="plan", choices=["plan", "investigation", "design", "migration"])
    new.add_argument("--outcome", default="")
    new.add_argument("--non-goals", default="")
    add = plan_sub.add_parser("add-slice")
    add.add_argument("--plan", required=True)
    add.add_argument("--id", required=True)
    add.add_argument("--scope", required=True)
    add.add_argument("--verification", required=True)
    slice_parser = plan_sub.add_parser("set-slice")
    slice_parser.add_argument("--plan", required=True)
    slice_parser.add_argument("--id", required=True)
    slice_parser.add_argument("--status", required=True, choices=["planned", "in-progress", "landed", "blocked"])
    slice_parser.add_argument("--evidence", default="")
    status = plan_sub.add_parser("status")
    status.add_argument("--plan", required=True)
    status.add_argument("--status", required=True, choices=["draft", "in-progress", "dev-finished", "blocked", "superseded", "abandoned"])
    status.add_argument("--blocker", default="")
    status.add_argument("--successor", default="")
    retire = plan_sub.add_parser("retire")
    retire.add_argument("--plan", required=True)

    decision = sub.add_parser("decision", help="Record a durable ruling")
    decision_sub = decision.add_subparsers(dest="decision_command", required=True)
    add_decision = decision_sub.add_parser("add")
    add_decision.add_argument("title")
    add_decision.add_argument("--module", required=True)
    add_decision.add_argument("--decision", required=True, choices=["accepted", "rejected", "deferred", "superseded"])
    add_decision.add_argument("--context", required=True)
    add_decision.add_argument("--ruling", required=True)
    add_decision.add_argument("--consequences", required=True)
    add_decision.add_argument("--reopen-if", default="")
    add_decision.add_argument("--enforced-by", action="append", default=[])

    verify = sub.add_parser("verify", help="Manage manual verification")
    verify_sub = verify.add_subparsers(dest="verify_command", required=True)
    add_verify = verify_sub.add_parser("add")
    add_verify.add_argument("title")
    add_verify.add_argument("--module", required=True)
    add_verify.add_argument("--source", default="")
    add_verify.add_argument("--issue", default="")
    add_verify.add_argument("--create-issue", action="store_true")
    close_verify = verify_sub.add_parser("close")
    close_verify.add_argument("--id", required=True)
    close_verify.add_argument("--verified-in", required=True)
    close_verify.add_argument("--confirmed-by", required=True)
    close_verify.add_argument("--evidence", default="")
    close_verify.add_argument("--close-issue", action="store_true")

    test = sub.add_parser("test", help="Select or run likely affected tests")
    test_sub = test.add_subparsers(dest="test_command", required=True)
    select = test_sub.add_parser("select")
    select.add_argument("--base")
    select.add_argument("--run", action="store_true")
    select.add_argument("--json", action="store_true")
    return parser


def _write_output(text: str, output: str | None) -> None:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="" if text.endswith("\n") else "\n")


def dispatch(args: argparse.Namespace, root: Path) -> int:
    if args.command == "discover":
        config = discover(root)
        text = dump_config(config)
        if args.stdout:
            print(text, end="")
            return 0
        output = root / args.output
        if output.exists() and not args.force:
            raise ValueError(f"{args.output} already exists; review it or use --force explicitly")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8", newline="\n")
        print(f"Wrote {args.output}. Review module boundaries, languages, commands, and existing instructions before init.")
        return 0

    if args.command == "init":
        config_path = root / args.config
        if not config_path.exists():
            raise ValueError(f"Missing {args.config}. Run 'aeng discover' first.")
        config = yaml.safe_load(config_path.read_text(encoding="utf-8-sig")) or {}
        validate_config(config)
        print(initialize_project(root, config, args.adopt_existing, args.dry_run))
        return 0

    if args.command == "check":
        errors, warnings = validate(root)
        for warning in warnings:
            print(f"WARN  {warning}")
        for error in errors:
            print(f"FAIL  {error}")
        if errors:
            print(f"\nGovernance check failed: {len(errors)} error(s), {len(warnings)} warning(s).")
            return 1
        print(f"Governance check passed: 0 error(s), {len(warnings)} warning(s).")
        return 0

    if args.command == "index":
        update_indexes(root)
        print("Regenerated plan, decision, manual-test, and project indexes.")
        return 0

    if args.command == "report":
        data = collect_report(root)
        text = render_json(data) if args.json else render_markdown(data)
        if args.output:
            output_path = Path(args.output)
            _write_output(text, str(output_path if output_path.is_absolute() else root / output_path))
        else:
            print(text, end="" if text.endswith("\n") else "\n")
        return 0

    if args.command == "plan":
        if args.plan_command == "new":
            path = create_plan(root, args.title, args.module, args.type, args.outcome, args.non_goals)
        elif args.plan_command == "add-slice":
            add_slice(root, args.plan, args.id, args.scope, args.verification)
            print(f"Added slice {args.id} to {args.plan}.")
            return 0
        elif args.plan_command == "set-slice":
            set_slice(root, args.plan, args.id, args.status, args.evidence)
            print(f"Updated slice {args.id} in {args.plan}.")
            return 0
        elif args.plan_command == "status":
            set_plan_status(root, args.plan, args.status, args.blocker, args.successor)
            print(f"Set {args.plan} to {args.status}.")
            return 0
        else:
            retire_plan(root, args.plan)
            print(f"Retired {args.plan}. Durable knowledge must live in decisions, docs, or technical notes.")
            return 0
        print(f"Created {path.relative_to(root).as_posix()}.")
        return 0

    if args.command == "decision":
        path = create_decision(
            root, args.title, args.module, args.decision, args.context, args.ruling,
            args.consequences, args.reopen_if, args.enforced_by,
        )
        print(f"Created {path.relative_to(root).as_posix()}.")
        return 0

    if args.command == "verify":
        if args.verify_command == "add":
            path = create_manual_test(root, args.title, args.module, args.source, args.issue, args.create_issue)
            print(f"Created {path.relative_to(root).as_posix()}.")
            return 0
        close_manual_test(root, args.id, args.verified_in, args.confirmed_by, args.evidence, args.close_issue)
        print(f"Marked {args.id} verified in {args.verified_in}.")
        return 0

    if args.command == "test":
        config = load_config(root)
        selection = select_tests(root, config, args.base)
        if args.json:
            print(json.dumps(selection, indent=2, ensure_ascii=False))
        else:
            print(f"Changed files: {len(selection['files'])}")
            print(f"Areas: {', '.join(selection['areas']) or 'none'}")
            print(f"Reason: {selection['reason']}")
            print(f"Command: {selection['command'] or '(not configured)'}")
            if selection["fallback"]:
                print("Fallback: selection was not considered sufficient.")
        if args.run and selection["command"]:
            return run_selection(root, selection)
        if args.run and selection["reason"] == "no production source changes detected":
            print("No production source changes; no tests required.")
            return 0
        return 0 if selection["command"] or selection["reason"] == "no production source changes detected" else 2
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        return dispatch(args, root)
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
