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
    "skill/SKILL.md",
]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*$")


def prose_lines(path):
    fenced = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield line


def anchors(path):
    slugs = set()
    for line in prose_lines(path):
        match = HEADING_RE.match(line)
        if match:
            slugs.add(re.sub(r"[^\w\- ]", "", match.group(1).lower()).replace(" ", "-"))
    return slugs


def local_links(path):
    for line in prose_lines(path):
        for link in LINK_RE.findall(line):
            if not re.match(r"^[a-z]+://", link) and not link.startswith("mailto:"):
                yield link.partition("#")[::2]


class DocsTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        missing = []
        for name in DOCS:
            path = ROOT / name
            for target, anchor in local_links(path):
                resolved = path.parent / target if target else path
                if not resolved.exists():
                    missing.append("%s -> %s" % (name, target))
                elif anchor and resolved.suffix == ".md" and anchor not in anchors(resolved):
                    missing.append("%s -> %s#%s" % (name, target, anchor))

        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
