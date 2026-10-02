import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "citation-fixer/scripts/validate_citations.py"
spec = importlib.util.spec_from_file_location("citations", SCRIPT)
citations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(citations)


class CitationTests(unittest.TestCase):
    def test_all_documented_type_fixtures(self):
        fixtures = json.loads((ROOT / "citation-fixer/references/citation-fixtures.json").read_text())["cases"]
        for case in fixtures:
            with self.subTest(case=case["id"]):
                self.assertEqual(not citations.validate(case["citation"]), case["valid_syntax"])
        for kind in citations.FIELDS:
            self.assertEqual({case["valid_syntax"] for case in fixtures if case["type"] == kind}, {True, False})

    def test_audit_locations_and_read_only_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "note with spaces.md"
            content = 'Original voice.\nClaim [Source: paper, A. Example, "Title", 2024]\nOther [Source: synthesis, compiled from ]\n'
            note.write_text(content)
            findings = citations.audit(note)
            self.assertEqual([(r["line"], r["column"], r["valid_syntax"]) for r in findings], [(2, 7, True), (3, 7, False)])
            result = subprocess.run([sys.executable, str(SCRIPT), str(note)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(len(json.loads(result.stdout)["citations"]), 2)
            self.assertEqual(note.read_text(), content)

    def test_valid_syntax_does_not_claim_source_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "source.md"
            note.write_text('[Source: synthesis, compiled from missing-source]\nAn uncited claim.\n')
            result = subprocess.run([sys.executable, str(SCRIPT), str(note)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(len(json.loads(result.stdout)["citations"]), 1)
            self.assertTrue(citations.validate('[Source: user, context, 2026-10-02][unexpected]'))


if __name__ == "__main__":
    unittest.main()
