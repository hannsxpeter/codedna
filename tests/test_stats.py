import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATS_PATH = ROOT / "skill" / "scripts" / "codedna_stats.py"


def load_stats():
    spec = importlib.util.spec_from_file_location("codedna_stats", STATS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StatsTests(unittest.TestCase):
    def setUp(self):
        self.stats = load_stats()

    def test_case_classification(self):
        self.assertEqual(self.stats.case("main"), "lower")
        self.assertEqual(self.stats.case("loadUser"), "camelCase")
        self.assertEqual(self.stats.case("LoadUser"), "PascalCase")
        self.assertEqual(self.stats.case("load_user"), "snake_case")
        self.assertEqual(self.stats.case("MAX_RETRY"), "SCREAMING_SNAKE")
        self.assertEqual(self.stats.case("tiny-worker"), "kebab")

    def test_js_arrow_detection_skips_parenthesized_initializer(self):
        results = {item["language"]: item for item in self.stats.analyze(ROOT / "tests" / "fixtures" / "terse_js")}
        js = results["js"]

        functions = js["naming"]["function"]
        self.assertEqual(sum(functions.values()), 4)
        self.assertEqual(functions["camelCase"], 3)
        self.assertEqual(functions["lower"], 1)

    def test_js_reports_backticks(self):
        results = {item["language"]: item for item in self.stats.analyze(ROOT / "tests" / "fixtures" / "terse_js")}
        quotes = results["js"]["quotes"]

        self.assertEqual(quotes["double"], 1)
        self.assertEqual(quotes["single"], 1)
        self.assertEqual(quotes["backtick"], 1)

    def test_go_quote_output_is_suppressed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "main.go"
            path.write_text("package main\n\nconst marker = 'x'\n", encoding="utf-8")
            results = {item["language"]: item for item in self.stats.analyze(tmp)}

        self.assertEqual(results["go"]["quotes"], {})

    def test_json_cli_output(self):
        proc = subprocess.run(
            [sys.executable, str(STATS_PATH), "--json", str(ROOT / "tests" / "fixtures" / "chatty_py")],
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(proc.stdout)

        self.assertEqual(payload[0]["language"], "py")
        self.assertIn("function", payload[0]["naming"])
        self.assertIn("function_lengths", payload[0])
        self.assertGreater(payload[0]["function_lengths"]["median"], 0)
        self.assertIn("identifier_lengths", payload[0])
        self.assertEqual(payload[0]["doc_comment_coverage"]["functions"], 3)
        self.assertEqual(payload[0]["doc_comment_coverage"]["documented"], 1)

    def test_reports_deeper_style_metrics(self):
        results = {item["language"]: item for item in self.stats.analyze(ROOT / "tests" / "fixtures" / "terse_js")}
        js = results["js"]

        self.assertEqual(js["function_lengths"]["count"], 4)
        self.assertGreaterEqual(js["function_lengths"]["p90"], js["function_lengths"]["median"])
        self.assertGreater(js["identifier_lengths"]["function"]["median"], 0)
        self.assertGreater(js["boolean_prefix_share"]["prefixed"], 0)

    def test_midline_string_terminator_is_not_a_docstring(self):
        text = 'SQL = """\nSELECT 1\n"""\n\n\ndef load():\n    return 1\n'

        code, comment, _, _ = self.stats.count_lines("py", text)

        self.assertEqual((code, comment), (5, 0))

    def test_docstring_still_counts_as_comment(self):
        code, comment, _, _ = self.stats.count_lines("py", '"""Module doc."""\nimport os\n')

        self.assertEqual((code, comment), (1, 1))

    def test_quoted_triple_and_hash_mention_do_not_open_a_block(self):
        quoted = "SEP = '\"\"\"'\nvalue = 1\n"
        mention = '# use """ to open a docstring\nvalue = 1\n'

        self.assertEqual(self.stats.count_lines("py", quoted)[:2], (2, 0))
        self.assertEqual(self.stats.count_lines("py", mention)[:2], (1, 1))

    def test_url_glob_in_line_comment_does_not_open_a_block(self):
        text = "// handler (/api/auth/*), served by Convex\n// second comment\nconst y = 2;\n"

        code, comment, _, _ = self.stats.count_lines("js", text)

        self.assertEqual((code, comment), (1, 2))

    def test_blank_lines_inside_a_block_comment_are_not_counted(self):
        text = "/* first\n\n   second */\nconst y = 2;\n"

        code, comment, _, _ = self.stats.count_lines("js", text)

        self.assertEqual((code, comment), (1, 2))

    def test_multiline_jsdoc_counts_as_documentation(self):
        text = "/**\n * Adds two numbers.\n */\nfunction add(a, b) { return a + b; }\n\nfunction bare() {}\n"

        self.assertEqual(self.stats.doc_coverage("js", text), (1, 2))

    def test_plain_line_comment_is_not_documentation_outside_go(self):
        text = "// plain aside\nfunction four() {}\n\nfunction bare() {}\n"

        self.assertEqual(self.stats.doc_coverage("js", text), (0, 2))

    def test_plain_block_comment_is_not_documentation(self):
        text = "/* not a doc block */\nfunction three() {}\n\nfunction bare() {}\n"

        self.assertEqual(self.stats.doc_coverage("js", text), (0, 2))

    def test_go_treats_line_comments_as_doc_comments(self):
        text = "// Add returns a plus b.\nfunc Add(a, b int) int { return a + b }\n\nfunc Bare() {}\n"

        self.assertEqual(self.stats.doc_coverage("go", text), (1, 2))

    def test_tab_indented_python_functions_are_measured(self):
        text = "def first():\n\tvalue = 1\n\treturn value\n\ndef second():\n\treturn 2\n"

        self.assertEqual(self.stats.py_function_lengths(text), [3, 2])

    def test_boolean_prefix_requires_a_word_boundary(self):
        prefixed = ["isReady", "has_items", "did_run", "will_retry"]
        plain = ["issue", "cannot", "island", "hash"]

        self.assertTrue(all(self.stats.BOOLEAN_PREFIX_RE.match(name) for name in prefixed))
        self.assertFalse(any(self.stats.BOOLEAN_PREFIX_RE.match(name) for name in plain))

    def test_byte_order_mark_does_not_hide_the_first_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "marked.py"
            path.write_text('"""Doc."""\n\n\ndef load():\n    return 1\n', encoding="utf-8-sig")
            results = {item["language"]: item for item in self.stats.analyze(tmp)}

        self.assertEqual(results["py"]["naming"]["function"], {"lower": 1})
        self.assertEqual(results["py"]["comment_lines"], 1)

    def test_minified_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.js").write_text("const loadUser = () => 1;\n", encoding="utf-8")
            (root / "bundle.js").write_text("const a=1;" * 200 + "\n", encoding="utf-8")
            results = {item["language"]: item for item in self.stats.analyze(tmp)}

        self.assertEqual(results["js"]["files_read"], 1)
        self.assertEqual(results["js"]["files_skipped_minified"], 1)


if __name__ == "__main__":
    unittest.main()
