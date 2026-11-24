from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from aeng.config import discover, dump_config, validate_config
from aeng.docs import (
    check_documentation,
    documentation_impact,
    initialize_docs,
    render_audit_markdown,
)
from aeng.initializer import initialize_project


class DocumentationCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src/core").mkdir(parents=True)
        (self.root / "src/other").mkdir(parents=True)
        (self.root / "src/core/logic.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.root / "src/other/other.py").write_text("VALUE = 2\n", encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "docs/index.md").write_text("# Manual\n\nSee [logic](../src/core/logic.py).\n", encoding="utf-8")
        self.config = discover(self.root)
        self.config["project"]["languages"] = ["python"]
        self.config["modules"] = [{"id": "core", "name": "Core", "paths": ["src/**"], "responsibility": "Source"}]
        self.config["documentation"] = {
            "root": "docs",
            "locales": ["en"],
            "translation_policy": "declared-only",
            "build_command": "",
            "pages": [{"path": "docs/index.md", "source_patterns": ["src/core/**"]}],
            "screenshots": {"index": "docs/screenshot-index.md", "required": False},
            "search_index": {"generated_at": "release", "committed": False},
        }
        (self.root / ".agent-engineering.yaml").write_text(dump_config(self.config), encoding="utf-8")
        initialize_project(self.root, self.config)

    def tearDown(self):
        self.temp.cleanup()

    def test_docs_init_preserves_existing_style(self):
        style = self.root / "docs/STYLE.md"
        style.write_text("# Existing style\n", encoding="utf-8")
        initialize_docs(self.root, self.config)
        self.assertEqual(style.read_text(encoding="utf-8"), "# Existing style\n")
        self.assertTrue((self.root / "docs/TRACEABILITY.md").exists())
        self.assertTrue((self.root / "docs/screenshot-index.md").exists())

    def test_check_accepts_valid_traceability_and_empty_screenshot_index(self):
        initialize_docs(self.root, self.config)
        page = self.root / "docs/index.md"
        page.write_text(
            "# Manual\n\n<!--\n  UI Source: src/core/logic.py (2026-11-24)\n-->\n",
            encoding="utf-8",
        )
        errors, warnings, metrics = check_documentation(self.root, self.config)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(metrics["pages"], 4)

    def test_check_rejects_missing_traceability_source(self):
        page = self.root / "docs/index.md"
        page.write_text("# Manual\n\n<!--\n  Code Source: src/missing.py\n-->\n", encoding="utf-8")
        errors, _, _ = check_documentation(self.root, self.config)
        self.assertTrue(any("Code Source does not resolve" in error for error in errors))

    def test_fenced_traceability_example_is_not_validated(self):
        page = self.root / "docs/guide.md"
        page.write_text("# Guide\n\n```html\n<!-- Code Source: src/missing.py -->\n```\n", encoding="utf-8")
        errors, _, _ = check_documentation(self.root, self.config)
        self.assertEqual(errors, [])

    def test_verified_screenshot_requires_build(self):
        (self.root / "docs/images").mkdir()
        (self.root / "docs/images/example.png").write_bytes(b"png")
        (self.root / "docs/index.md").write_text("# Manual\n\n![Example](images/example.png)\n", encoding="utf-8")
        (self.root / "docs/screenshot-index.md").write_text(
            "# Screenshot index\n\n## Screenshots\n\n"
            "| Doc page | UI source | Asset | Status | Must show | Verified in |\n"
            "|---|---|---|---|---|---|\n"
            "| index.md | src/core/logic.py | images/example.png | verified | Full window | — |\n",
            encoding="utf-8",
        )
        errors, _, _ = check_documentation(self.root, self.config)
        self.assertTrue(any("verified requires verified_in" in error for error in errors))

    def test_current_technical_note_requires_source_and_review(self):
        note = self.root / "engineering/technical/architecture.md"
        note.write_text(
            "---\nid: architecture\nstatus: current\nupdated: 2026-11-24\n"
            "reviewed_against: ''\nowners: [core]\nsource_paths: []\n---\n\n# Architecture\n",
            encoding="utf-8",
        )
        errors, _, _ = check_documentation(self.root, self.config)
        self.assertTrue(any("requires reviewed_against" in error for error in errors))
        self.assertTrue(any("requires source_paths" in error for error in errors))

    def test_impact_maps_pages_gaps_screenshots_and_unmapped_source(self):
        subprocess.run(["git", "init"], cwd=self.root, check=True, capture_output=True)
        (self.root / "src/core/logic.py").write_text("VALUE = 3\n", encoding="utf-8")
        (self.root / "src/other/other.py").write_text("VALUE = 4\n", encoding="utf-8")
        self.config["documentation"]["pages"].append({"path": "docs/missing.md", "source_patterns": ["src/core/**"]})
        (self.root / ".agent-engineering.yaml").write_text(dump_config(self.config), encoding="utf-8")
        (self.root / "docs/screenshot-index.md").write_text(
            "# Screenshot index\n\n## Screenshots\n\n"
            "| Doc page | UI source | Asset | Status | Must show | Verified in |\n"
            "|---|---|---|---|---|---|\n"
            "| index.md | src/core/logic.py | images/example.png | placeholder | Full window | — |\n",
            encoding="utf-8",
        )
        data = documentation_impact(self.root, self.config)
        self.assertIn("docs/index.md", [item["path"] for item in data["impacted_pages"]])
        self.assertIn("docs/missing.md", data["doc_gaps"])
        self.assertIn("src/other/other.py", data["unmapped_source"])
        self.assertEqual(data["screenshots"][0]["status"], "placeholder")

    def test_audit_contains_human_semantic_review(self):
        report = render_audit_markdown(self.root, self.config)
        self.assertIn("Required human review", report)
        self.assertIn("cannot certify that prose is semantically true", report)

    def test_configured_page_outside_docs_root_is_checked(self):
        self.config["documentation"]["pages"].append({"path": "README.md", "source_patterns": []})
        (self.root / "README.md").write_text("# Readme\n\n[Missing](missing.md)\n", encoding="utf-8")
        errors, _, _ = check_documentation(self.root, self.config)
        self.assertTrue(any("README.md: dead link -> missing.md" in error for error in errors))

    def test_invalid_documentation_config_is_rejected(self):
        self.config["documentation"]["pages"] = [{"source_patterns": []}]
        with self.assertRaises(ValueError):
            validate_config(self.config)


if __name__ == "__main__":
    unittest.main()
