import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIRE_PATH = ROOT / "skill" / "scripts" / "codedna_wire.py"


def load_wire():
    spec = importlib.util.spec_from_file_location("codedna_wire", WIRE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WireTests(unittest.TestCase):
    def setUp(self):
        self.wire = load_wire()

    def test_default_creates_agents_and_updates_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude = root / "CLAUDE.md"
            claude.write_text("# Existing\n\nKeep this.\n", encoding="utf-8")

            results = self.wire.wire(root)

            paths = {item["target"]: Path(item["path"]) for item in results}
            self.assertIn("agents", paths)
            self.assertIn("claude", paths)
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertIn("Keep this.", claude.read_text(encoding="utf-8"))
            self.assertIn("<!-- codedna:start -->", claude.read_text(encoding="utf-8"))
            self.assertIn("code or repository prose", claude.read_text(encoding="utf-8"))

    def test_replaces_existing_block_without_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text(
                "# Existing\n\n<!-- codedna:start -->\nold\n<!-- codedna:end -->\n\nAfter.\n",
                encoding="utf-8",
            )

            self.wire.wire(root)
            self.wire.wire(root)
            text = agents.read_text(encoding="utf-8")

            self.assertEqual(text.count("<!-- codedna:start -->"), 1)
            self.assertEqual(text.count("<!-- codedna:end -->"), 1)
            self.assertNotIn("\nold\n", text)
            self.assertIn("After.", text)

    def test_all_creates_agent_specific_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = self.wire.wire(root, all_targets=True)
            targets = {item["target"] for item in results}

            self.assertEqual({"agents", "claude", "gemini", "copilot", "cursor", "cascade"}, targets)
            self.assertTrue((root / ".github/copilot-instructions.md").exists())
            self.assertTrue((root / ".cursor/rules/codedna.mdc").exists())
            self.assertTrue((root / ".devin/rules/codedna.md").exists())
            self.assertIn("alwaysApply: true", (root / ".cursor/rules/codedna.mdc").read_text(encoding="utf-8"))
            self.assertIn("trigger: always_on", (root / ".devin/rules/codedna.md").read_text(encoding="utf-8"))

    def test_uses_legacy_windsurf_rules_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".windsurf/rules").mkdir(parents=True)

            self.wire.wire(root, targets=["cascade"])

            self.assertTrue((root / ".windsurf/rules/codedna.md").exists())
            self.assertFalse((root / ".devin/rules/codedna.md").exists())

    def test_repeated_wiring_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"

            self.wire.wire(root)
            first = agents.read_bytes()
            self.wire.wire(root)
            self.wire.wire(root)

            self.assertEqual(first, agents.read_bytes())

    def test_preserves_indentation_after_the_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text(
                "# Doc\n\n<!-- codedna:start -->\nold\n<!-- codedna:end -->\n\n    indented = 1\n",
                encoding="utf-8",
            )

            self.wire.wire(root)

            self.assertIn("\n    indented = 1\n", agents.read_text(encoding="utf-8"))

    def test_stray_end_marker_does_not_duplicate_the_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text(
                "<!-- codedna:end -->\n\nintro\n\n<!-- codedna:start -->\nold\n<!-- codedna:end -->\n",
                encoding="utf-8",
            )

            self.wire.wire(root)
            self.wire.wire(root)
            text = agents.read_text(encoding="utf-8")

            self.assertEqual(text.count("<!-- codedna:start -->"), 1)
            self.assertIn("intro", text)

    def test_lone_start_marker_is_left_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text("# Doc\n\n<!-- codedna:start -->\n\nTail.\n", encoding="utf-8")

            self.wire.wire(root)
            self.wire.wire(root)
            text = agents.read_text(encoding="utf-8")

            self.assertIn("Tail.", text)
            self.assertEqual(text.count("<!-- codedna:end -->"), 1)

    def test_lone_start_marker_does_not_swallow_a_foreign_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text(
                "# Doc\n\n<!-- codedna:start -->\n\n"
                "<!-- other:start -->\nforeign\n<!-- other:end -->\n\nTail.\n",
                encoding="utf-8",
            )

            self.wire.wire(root)
            self.wire.wire(root)
            text = agents.read_text(encoding="utf-8")

            self.assertIn("Tail.", text)
            self.assertIn("<!-- other:start -->", text)
            self.assertIn("foreign", text)

    def test_start_marker_inside_the_replaced_body_keeps_the_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "AGENTS.md"
            agents.write_text(
                "# Doc\n\n<!-- codedna:start -->\n"
                "old body naming <!-- codedna:start --> inline\n"
                "<!-- codedna:end -->\n\nTail.\n",
                encoding="utf-8",
            )

            self.wire.wire(root)
            first = agents.read_text(encoding="utf-8")
            self.wire.wire(root)

            self.assertEqual(first, agents.read_text(encoding="utf-8"))
            self.assertIn("Tail.", first)
            self.assertIn("## Code and prose style", first)

    def test_replace_block_honors_custom_markers(self):
        text = (
            "<!-- codedna:start -->\nkeep\n<!-- codedna:end -->\n\n"
            "<!-- other:start -->\nstale\n<!-- other:end -->\n"
        )
        updated = self.wire.replace_block(
            text,
            "<!-- other:start -->\nfresh\n<!-- other:end -->\n",
            "<!-- other:start -->",
            "<!-- other:end -->",
        )

        self.assertIn("keep", updated)
        self.assertIn("fresh", updated)
        self.assertNotIn("stale", updated)

    def test_json_cli_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(WIRE_PATH), "--json", "--agent", "agents", tmp],
                check=True,
                text=True,
                capture_output=True,
            )
            payload = json.loads(proc.stdout)

            self.assertEqual(payload[0]["target"], "agents")
            self.assertTrue((Path(tmp) / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
