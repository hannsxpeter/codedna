#!/usr/bin/env python3
"""Best-effort style statistics for codedna."""

import argparse
import json
import os
import re
from collections import Counter, defaultdict

MAX_FILES_PER_LANG = 800
MAX_FILE_BYTES = 1_000_000

IGNORE = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "vendor",
    ".next",
    ".svelte-kit",
    "venv",
    ".venv",
    "__pycache__",
    "coverage",
}

EXT = {
    ".js": "js",
    ".jsx": "js",
    ".mjs": "js",
    ".cjs": "js",
    ".ts": "ts",
    ".tsx": "ts",
    ".py": "py",
    ".go": "go",
    ".rs": "rs",
    ".java": "java",
    ".rb": "rb",
    ".php": "php",
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "cs",
    ".swift": "swift",
    ".kt": "kt",
}

HASH_COMMENT = {"py", "rb"}
QUOTE_LANGS = {"js", "ts", "py", "rb", "php"}

PATS = {
    "js": {
        "function": [
            r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(",
            r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?function\b",
            r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>",
        ],
        "type": [r"\b(?:interface|type)\s+([A-Za-z_$][\w$]*)"],
        "class": [r"\bclass\s+([A-Za-z_$][\w$]*)"],
        "constant": [r"\bconst\s+([A-Z_][A-Z0-9_]{2,})\b"],
    },
    "py": {
        "function": [r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)"],
        "class": [r"^\s*class\s+([A-Za-z_]\w*)"],
        "constant": [r"^([A-Z_][A-Z0-9_]{2,})\s*="],
    },
    "go": {
        "function": [r"\bfunc\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)"],
        "type": [r"\btype\s+([A-Za-z_]\w*)"],
    },
    "rs": {
        "function": [r"\bfn\s+([A-Za-z_]\w*)"],
        "type": [r"\b(?:struct|enum|trait)\s+([A-Za-z_]\w*)"],
    },
}
PATS["ts"] = PATS["js"]


def case(name):
    text = name.strip("_")
    if not text:
        return "other"
    if "-" in text:
        return "kebab"
    if "_" in text:
        if text.isupper():
            return "SCREAMING_SNAKE"
        if text.islower():
            return "snake_case"
        return "mixed"
    if text.isupper():
        return "UPPER"
    if text.islower():
        return "lower"
    return "PascalCase" if text[0].isupper() else "camelCase"


def collect_files(target):
    files = defaultdict(list)
    for root, dirs, names in os.walk(target):
        dirs[:] = [d for d in dirs if d not in IGNORE and not d.startswith(".")]
        for name in names:
            lang = EXT.get(os.path.splitext(name)[1].lower())
            if lang:
                files[lang].append(os.path.join(root, name))
    return files


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def comment_config(lang):
    token = "#" if lang in HASH_COMMENT else "//"
    if lang == "py":
        block = [('"""', '"""'), ("'''", "'''")]
    elif lang in HASH_COMMENT:
        block = []
    else:
        block = [("/*", "*/")]
    return token, block


def count_lines(lang, text):
    token, block = comment_config(lang)
    code = comment = tabs = spaces = 0
    in_block = None
    for line in text.splitlines():
        stripped = line.strip()
        if in_block is not None:
            comment += 1
            if in_block in line:
                in_block = None
            continue
        if not stripped:
            continue
        hit = False
        for opener, closer in block:
            if stripped.startswith(opener):
                comment += 1
                if closer not in stripped[len(opener):]:
                    in_block = closer
                hit = True
                break
        if hit:
            continue
        if stripped.startswith(token):
            comment += 1
            continue
        code += 1
        leading = line[: len(line) - len(line.lstrip())]
        if leading.startswith("\t"):
            tabs += 1
        elif leading.startswith(" "):
            spaces += 1
    return code, comment, tabs, spaces


def count_quotes(lang, text):
    if lang not in QUOTE_LANGS:
        return Counter()
    counts = Counter()
    counts["double"] = len(re.findall(r'"(?:[^"\\]|\\.)*"', text))
    counts["single"] = len(re.findall(r"'(?:[^'\\]|\\.)*'", text))
    if lang in {"js", "ts"}:
        counts["backtick"] = len(re.findall(r"`(?:[^`\\]|\\.)*`", text, re.S))
    return counts


def add_file_case(naming, path):
    base = os.path.splitext(os.path.basename(path))[0]
    if base:
        naming["file"][case(base)] += 1


def add_identifier_cases(lang, text, naming):
    for kind, patterns in PATS.get(lang, {}).items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.M):
                naming[kind][case(match.group(1))] += 1


def analyze_language(lang, paths):
    result = {
        "language": lang,
        "files_total": len(paths),
        "files_read": 0,
        "files_skipped_large": 0,
        "read_errors": 0,
        "code_lines": 0,
        "comment_lines": 0,
        "indent": {"tabs": 0, "spaces": 0, "style": "spaces"},
        "quotes": {},
        "naming": {},
    }
    naming = defaultdict(Counter)
    quotes = Counter()

    for path in paths[:MAX_FILES_PER_LANG]:
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                result["files_skipped_large"] += 1
                continue
            text = read_text(path)
        except OSError:
            result["read_errors"] += 1
            continue

        result["files_read"] += 1
        code, comment, tabs, spaces = count_lines(lang, text)
        result["code_lines"] += code
        result["comment_lines"] += comment
        result["indent"]["tabs"] += tabs
        result["indent"]["spaces"] += spaces
        quotes.update(count_quotes(lang, text))
        add_file_case(naming, path)
        add_identifier_cases(lang, text, naming)

    result["files_capped"] = max(len(paths) - MAX_FILES_PER_LANG, 0)
    total_lines = result["code_lines"] + result["comment_lines"]
    result["comment_density"] = round(100 * result["comment_lines"] / total_lines, 1) if total_lines else 0
    result["indent"]["style"] = "tabs" if result["indent"]["tabs"] > result["indent"]["spaces"] else "spaces"
    result["quotes"] = dict(quotes)
    result["naming"] = {kind: dict(counter) for kind, counter in naming.items()}
    return result


def analyze(target):
    files = collect_files(target)
    return [
        analyze_language(lang, paths)
        for lang, paths in sorted(files.items(), key=lambda item: -len(item[1]))
    ]


def pct(counter, key):
    total = sum(counter.values())
    return round(100 * counter[key] / total) if total else 0


def print_text(results, target):
    if not results:
        print("No recognized source files under", target)
        return

    for result in results:
        lang = result["language"]
        total = result["files_total"]
        read = result["files_read"]
        if read == total:
            sample = "%d files" % total
        else:
            sample = "read %d of %d files" % (read, total)
        print("\n== %s (%s, %d code lines) ==" % (lang, sample, result["code_lines"]))
        if result["files_capped"]:
            print("  sampled  : capped at %d files" % MAX_FILES_PER_LANG)
        if result["files_skipped_large"]:
            print("  skipped  : %d oversized files" % result["files_skipped_large"])
        if result["read_errors"]:
            print("  unread   : %d files" % result["read_errors"])
        print("  comments : %s%% of non-blank lines" % result["comment_density"])
        print(
            "  indent   : %s (tabs %d / spaces %d indented lines)"
            % (
                result["indent"]["style"],
                result["indent"]["tabs"],
                result["indent"]["spaces"],
            )
        )

        quotes = Counter(result["quotes"])
        if quotes:
            parts = ["%s %d%%" % (name, pct(quotes, name)) for name in ["double", "single", "backtick"] if quotes.get(name)]
            print("  quotes   : " + " / ".join(parts))

        for kind, counts in result["naming"].items():
            counter = Counter(counts)
            total_names = sum(counter.values())
            if not total_names:
                continue
            top = ", ".join(
                "%s %d%%" % (name, round(100 * count / total_names))
                for name, count in counter.most_common(3)
            )
            print("  %-9s: %s" % (kind, top))
        if any("lower" in counts for counts in result["naming"].values()):
            print("  note     : lower means single-word names compatible with snake_case or camelCase")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print best-effort code style statistics.")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    results = analyze(args.target)
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print_text(results, args.target)


if __name__ == "__main__":
    main()
