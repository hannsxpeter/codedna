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


if __name__ == "__main__":
    unittest.main()
