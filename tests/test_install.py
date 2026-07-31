import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "SKILL.md"
SUPPORT = ROOT / "docs" / "AGENT_SUPPORT.md"
VERSION = re.search(r"^Version: (\S+)$", SKILL.read_text(encoding="utf-8"), re.M).group(1)
SEMVER_RE = re.compile(r"\d+\.\d+\.\d+")


class InstallTests(unittest.TestCase):
    def test_install_without_target_prints_usage_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "codex"

            env = os.environ.copy()
            env["CODEX_SKILLS_DIR"] = str(dest)
            proc = subprocess.run(
                [str(ROOT / "install.sh")],
                cwd=ROOT,
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertIn("Usage: ./install.sh <all|claude|codex|cursor|windsurf>", proc.stderr)
            self.assertFalse(dest.exists())

    def test_install_all_writes_supported_skill_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude = root / "claude"
            codex = root / "codex"
            cursor = root / "cursor"
            windsurf = root / "windsurf"
            claude.mkdir()
            codex.mkdir()
            cursor.mkdir()
            windsurf.mkdir()
            stale = claude / "codedna.md"
            stale.write_text("old install\n", encoding="utf-8")

            env = os.environ.copy()
            env["CLAUDE_SKILLS_DIR"] = str(claude)
            env["CODEX_SKILLS_DIR"] = str(codex)
            env["CURSOR_SKILLS_DIR"] = str(cursor)
            env["WINDSURF_SKILLS_DIR"] = str(windsurf)
            proc = subprocess.run(
                [str(ROOT / "install.sh"), "all"],
                cwd=ROOT,
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )

            for dest in [claude, codex, cursor, windsurf]:
                skill = dest / "codedna" / "SKILL.md"
                script = dest / "codedna" / "scripts" / "codedna_stats.py"
                wire = dest / "codedna" / "scripts" / "codedna_wire.py"
                mode = script.stat().st_mode
                wire_mode = wire.stat().st_mode

                self.assertTrue(skill.exists())
                self.assertTrue(script.exists())
                self.assertTrue(wire.exists())
                self.assertTrue(mode & stat.S_IXUSR)
                self.assertTrue(wire_mode & stat.S_IXUSR)
            self.assertFalse(stale.exists())
            for label in ["Claude Code", "Codex", "Cursor", "Windsurf/Cascade"]:
                self.assertIn("Installed codedna v%s for %s" % (VERSION, label), proc.stdout)

    def test_install_single_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "codex"

            env = os.environ.copy()
            env["CODEX_SKILLS_DIR"] = str(dest)
            proc = subprocess.run(
                [str(ROOT / "install.sh"), "codex"],
                cwd=ROOT,
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertTrue((dest / "codedna" / "SKILL.md").exists())
            self.assertIn("Installed codedna v%s for Codex" % VERSION, proc.stdout)

    def test_version_is_consistent_across_skill_and_docs(self):
        found = set()
        for path in [SKILL, SUPPORT]:
            found.update(SEMVER_RE.findall(path.read_text(encoding="utf-8")))

        self.assertEqual({VERSION}, found)


if __name__ == "__main__":
    unittest.main()
