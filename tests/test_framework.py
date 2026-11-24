from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from aeng.config import discover, dump_config, load_config
from aeng.documents import parse_document, write_document
from aeng.indexes import update_indexes
from aeng.initializer import initialize_project
from aeng.lifecycle import (
    add_slice,
    close_manual_test,
    create_decision,
    create_manual_test,
    create_plan,
    retire_plan,
    set_plan_status,
    set_slice,
)
from aeng.report import collect_report
from aeng.test_selector import select_tests
from aeng.validator import validate


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src/core").mkdir(parents=True)
        (self.root / "src/core/logic.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests/test_logic.py").write_text("import unittest\n", encoding="utf-8")
        self.config = discover(self.root)
        self.config["project"]["name"] = "Sample"
        self.config["project"]["languages"] = ["python"]
        (self.root / ".agent-engineering.yaml").write_text(dump_config(self.config), encoding="utf-8")
        initialize_project(self.root, self.config)

    def tearDown(self):
        self.temp.cleanup()

    def errors(self):
        errors, _ = validate(self.root)
        return errors


class InitializationTests(ProjectCase):
    def test_clean_initialization_passes(self):
        self.assertEqual(self.errors(), [])
        self.assertTrue((self.root / "AGENTS.md").exists())
        self.assertTrue((self.root / "CLAUDE.md").exists())
        self.assertTrue((self.root / ".github/instructions/agent-engineering/testing.md").exists())
        self.assertFalse((self.root / ".github/instructions/agent-engineering/agent-engineering").exists())
        self.assertFalse((self.root / ".agent-engineering/integration-block.md").exists())

    def test_existing_agent_files_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# Existing rules\n\nRead AGENTS.md.\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("# Existing Claude rules\n", encoding="utf-8")
            custom = root / ".github/instructions/custom.md"
            custom.parent.mkdir(parents=True)
            custom.write_text("# Custom instructions\n", encoding="utf-8")
            config = discover(root)
            config["project"]["languages"] = ["python"]
            (root / ".agent-engineering.yaml").write_text(dump_config(config), encoding="utf-8")
            initialize_project(root, config)
            self.assertIn("# Existing rules", (root / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertIn("# Existing Claude rules", (root / "CLAUDE.md").read_text(encoding="utf-8"))
            self.assertEqual(custom.read_text(encoding="utf-8"), "# Custom instructions\n")
            self.assertTrue((root / ".agent-engineering/integration-block.md").exists())
            self.assertTrue((root / ".agent-engineering/adoption-report.md").exists())

    def test_existing_engineering_requires_explicit_adoption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "engineering").mkdir()
            (root / "engineering/notes.md").write_text("Keep me", encoding="utf-8")
            config = discover(root)
            config["project"]["languages"] = ["python"]
            with self.assertRaises(ValueError):
                initialize_project(root, config)
            initialize_project(root, config, adopt_existing=True)
            self.assertEqual((root / "engineering/notes.md").read_text(encoding="utf-8"), "Keep me")

    def test_discovery_finds_language_and_module(self):
        self.assertEqual(self.config["project"]["languages"], ["python"])
        self.assertIn("core", [item["id"] for item in self.config["modules"]])


class LifecycleTests(ProjectCase):
    def test_plan_progress_requires_evidence_and_retires(self):
        path = create_plan(self.root, "Add a total", "core", "plan", "Return a total", "No UI")
        add_slice(self.root, "add-a-total", "S2", "Expose the result", "Unit test")
        set_slice(self.root, "add-a-total", "S1", "in-progress")
        set_plan_status(self.root, "add-a-total", "in-progress")
        with self.assertRaises(ValueError):
            set_slice(self.root, "add-a-total", "S1", "landed")
        set_slice(self.root, "add-a-total", "S1", "landed", "tests/test_logic.py")
        set_slice(self.root, "add-a-total", "S2", "landed", "tests/test_api.py")
        data, body = parse_document(path)
        data["docs_impact"] = "not-required"
        data["decisions_captured"] = True
        write_document(path, data, body)
        retire_plan(self.root, "add-a-total")
        self.assertFalse(path.exists())
        self.assertEqual(self.errors(), [])

    def test_dev_finished_requires_pending_manual_entry(self):
        create_plan(self.root, "Visual polish", "core", "plan", "Improve spacing", "No behavior change")
        path = self.root / "engineering/plans/visual-polish.md"
        data, body = parse_document(path)
        data["manual_required"] = True
        write_document(path, data, body)
        set_slice(self.root, "visual-polish", "S1", "landed", "owner-reviewed build")
        with self.assertRaises(ValueError):
            set_plan_status(self.root, "visual-polish", "dev-finished")
        create_manual_test(self.root, "Check spacing", "core", "visual-polish", issue="12")
        set_plan_status(self.root, "visual-polish", "dev-finished")
        self.assertEqual(self.errors(), [])

    def test_decision_uses_stable_date_slug_id(self):
        path = create_decision(
            self.root, "Stable identifiers", "core", "accepted", "Labels change",
            "Automation ids stay stable", "Tests do not depend on copy", "A new id policy is approved",
            ["tests/test_logic.py"],
        )
        self.assertRegex(path.stem, r"^dec-\d{4}-\d{2}-\d{2}-stable-identifiers$")
        self.assertIn(path.name, (self.root / "engineering/decisions/README.md").read_text(encoding="utf-8"))
        self.assertEqual(self.errors(), [])

    def test_manual_verification_requires_issue_and_build(self):
        create_manual_test(self.root, "Check rendering", "core", "source", issue="")
        self.assertTrue(any("issue is required" in error for error in self.errors()))
        path = self.root / "engineering/manual-tests/check-rendering.md"
        data, body = parse_document(path)
        data["issue"] = "42"
        write_document(path, data, body)
        update_indexes(self.root)
        self.assertEqual(self.errors(), [])
        with self.assertRaises(ValueError):
            close_manual_test(self.root, "check-rendering", "", "owner", "screenshot")
        close_manual_test(self.root, "check-rendering", "abc123", "owner", "screenshot")
        self.assertEqual(self.errors(), [])
        self.assertNotIn("check-rendering.md", (self.root / "engineering/manual-tests/README.md").read_text(encoding="utf-8"))


class IndexAndReportTests(ProjectCase):
    def test_generated_index_drift_fails(self):
        create_plan(self.root, "Indexed work", "core", "plan", "Outcome", "Non-goals")
        path = self.root / "engineering/plans/INDEX.yaml"
        path.write_text("plans: []\n", encoding="utf-8")
        self.assertTrue(any("stale" in error for error in self.errors()))
        update_indexes(self.root)
        self.assertEqual(self.errors(), [])

    def test_report_derives_next_slice(self):
        create_plan(self.root, "Two slices", "core", "plan", "Outcome", "Non-goals")
        add_slice(self.root, "two-slices", "S2", "Second", "Test")
        set_slice(self.root, "two-slices", "S1", "landed", "commit abc")
        report = collect_report(self.root)
        plan = next(item for item in report["plans"] if item["id"] == "two-slices")
        self.assertEqual((plan["landed"], plan["total"], plan["next_slice"]), (1, 2, "S2"))

    def test_no_issue_tracker_can_disable_issue_requirement(self):
        self.config["github"]["issue_required"] = False
        (self.root / ".agent-engineering.yaml").write_text(dump_config(self.config), encoding="utf-8")
        create_manual_test(self.root, "Local-only check", "core", "source", issue="")
        self.assertEqual(self.errors(), [])

    def test_missing_test_matrix_fails(self):
        (self.root / "engineering/verification/test-matrix.yaml").unlink()
        self.assertTrue(any("test-matrix.yaml is missing" in error for error in self.errors()))

    def test_decision_title_collision_is_refused(self):
        arguments = dict(
            module="core", decision="accepted", context="Context", ruling="Ruling",
            consequences="Consequences", reopen_if="New evidence",
        )
        create_decision(self.root, "One ruling", **arguments)
        with self.assertRaises(ValueError):
            create_decision(self.root, "One ruling", **arguments)

    def test_expired_known_failure_blocks(self):
        path = self.root / "engineering/verification/known-failures.yaml"
        path.write_text(
            "failures:\n  - test_id: tests.old\n    owner: team\n    issue: '1'\n    reason: legacy\n    expires: 2000-01-01\n",
            encoding="utf-8",
        )
        self.assertTrue(any("expired" in error for error in self.errors()))


class TestSelectionTests(ProjectCase):
    def _git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, text=True, capture_output=True, check=True)

    def setUp(self):
        super().setUp()
        self._git("init")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test")
        self._git("add", ".")
        self._git("commit", "-m", "baseline")

    def test_untracked_source_file_is_selected(self):
        (self.root / "src/core/new.py").write_text("VALUE = 2\n", encoding="utf-8")
        selection = select_tests(self.root, load_config(self.root))
        self.assertIn("src/core/new.py", selection["files"])
        self.assertIn("core", selection["areas"])
        self.assertFalse(selection["fallback"])

    def test_unborn_head_includes_untracked_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src/core").mkdir(parents=True)
            (root / "src/core/first.py").write_text("VALUE = 1\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            selection = select_tests(root, discover(root))
            self.assertIn("src/core/first.py", selection["files"])
            self.assertIn("core", selection["areas"])

    def test_build_configuration_forces_fallback(self):
        (self.root / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
        selection = select_tests(self.root, load_config(self.root))
        self.assertTrue(selection["fallback"])
        self.assertIn("pyproject.toml", selection["reason"])


class SanitizationTests(unittest.TestCase):
    def test_published_sources_contain_no_private_project_identifiers(self):
        root = Path(__file__).resolve().parents[1]
        forbidden = ["ae" + "thrix", "aval" + "onia", "humming" + "bird", ".n" + "et 11"]
        paths = [root / "README.md", root / "README.fr.md", root / "README.zh-CN.md"]
        paths += list((root / "aeng").rglob("*"))
        paths += list((root / "docs").rglob("*.md"))
        paths += list((root / "examples").rglob("*"))
        for path in paths:
            if not path.is_file() or path.suffix not in {".md", ".py", ".yaml", ".yml", ".toml"}:
                continue
            text = path.read_text(encoding="utf-8-sig").lower()
            for token in forbidden:
                self.assertNotIn(token, text, f"private identifier in {path}")


if __name__ == "__main__":
    unittest.main()
