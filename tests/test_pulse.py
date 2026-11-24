from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aeng.config import discover, dump_config
from aeng.initializer import initialize_project
from aeng.lifecycle import create_plan, set_slice
from aeng.pulse import collect_pulse, render_pulse_markdown, write_pulse


class PulseCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src/core").mkdir(parents=True)
        (self.root / "src/core/logic.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "docs/index.md").write_text("# Manual\n", encoding="utf-8")
        self.config = discover(self.root)
        self.config["project"]["languages"] = ["python"]
        self.config["pulse"] = {"enabled": True, "stale_days": 7}
        (self.root / ".agent-engineering.yaml").write_text(dump_config(self.config), encoding="utf-8")
        initialize_project(self.root, self.config)

    def tearDown(self):
        self.temp.cleanup()

    def test_first_pulse_is_baseline_and_write_persists_json(self):
        latest, report, data = write_pulse(self.root, self.config)
        self.assertTrue(data["baseline"])
        self.assertEqual(data["changes"]["new_plans"], [])
        self.assertTrue(latest.exists())
        self.assertTrue(report.exists())
        saved = json.loads(latest.read_text(encoding="utf-8"))
        self.assertEqual(saved["version"], 1)
        self.assertIn("Documentation", render_pulse_markdown(saved))

    def test_second_pulse_detects_new_changed_and_retired_plans(self):
        create_plan(self.root, "First plan", "core", "plan", "Outcome", "Non-goals")
        write_pulse(self.root, self.config)
        set_slice(self.root, "first-plan", "S1", "landed", "tests/test_first.py")
        create_plan(self.root, "Second plan", "core", "plan", "Outcome", "Non-goals")
        data = collect_pulse(self.root, self.config)
        self.assertIn("second-plan", data["changes"]["new_plans"])
        self.assertEqual(data["changes"]["changed_plans"][0]["id"], "first-plan")
        self.assertFalse(data["baseline"])

    def test_pulse_includes_documentation_metrics(self):
        data = collect_pulse(self.root, self.config)
        self.assertTrue(data["documentation"]["configured"])
        self.assertGreaterEqual(data["documentation"]["pages"], 1)
        self.assertIn("screenshots", data["documentation"])

    def test_missing_baseline_after_delete_resets_comparison(self):
        write_pulse(self.root, self.config)
        (self.root / "engineering/pulse/latest.json").unlink()
        data = collect_pulse(self.root, self.config)
        self.assertTrue(data["baseline"])
        self.assertEqual(data["changes"]["new_plans"], [])


if __name__ == "__main__":
    unittest.main()
