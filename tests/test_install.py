import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def test_install_all_writes_supported_skill_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude = root / "claude"
            codex = root / "codex"
            windsurf = root / "windsurf"
            claude.mkdir()
            codex.mkdir()
            windsurf.mkdir()
            stale = claude / "codedna.md"
            stale.write_text("old install\n", encoding="utf-8")

            env = os.environ.copy()
            env["CLAUDE_SKILLS_DIR"] = str(claude)
            env["CODEX_SKILLS_DIR"] = str(codex)
            env["WINDSURF_SKILLS_DIR"] = str(windsurf)
            proc = subprocess.run(
                [str(ROOT / "install.sh")],
                cwd=ROOT,
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )

            for dest in [claude, codex, windsurf]:
                skill = dest / "codedna" / "SKILL.md"
                script = dest / "codedna" / "scripts" / "codedna_stats.py"
                mode = script.stat().st_mode

                self.assertTrue(skill.exists())
                self.assertTrue(script.exists())
                self.assertTrue(mode & stat.S_IXUSR)
            self.assertFalse(stale.exists())
            self.assertIn("Installed codedna v1.0.1 for Claude Code", proc.stdout)
            self.assertIn("Installed codedna v1.0.1 for Codex", proc.stdout)
            self.assertIn("Installed codedna v1.0.1 for Windsurf/Cascade", proc.stdout)

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
            self.assertIn("Installed codedna v1.0.1 for Codex", proc.stdout)


if __name__ == "__main__":
    unittest.main()
