import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    "README.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "docs/AGENT_SUPPORT.md",
]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def local_target(link):
    target = link.split("#", 1)[0]
    if not target:
        return None
    if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
        return None
    return target


class DocsTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        missing = []
        for name in DOCS:
            path = ROOT / name
            for link in LINK_RE.findall(path.read_text(encoding="utf-8")):
                target = local_target(link)
                if target and not (path.parent / target).exists():
                    missing.append("%s -> %s" % (name, target))

        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
