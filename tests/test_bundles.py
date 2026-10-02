import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bundles", ROOT / "scripts/check_bundles.py")
bundles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundles)


class BundleTests(unittest.TestCase):
    def test_markdown_examples_are_not_packaged_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "example"
            skill.mkdir()
            (skill / "real file.md").write_text("Reference")
            (skill / "SKILL.md").write_text('---\nname: example\ndescription: Example\n---\n'
                '```markdown\n[Example](missing.md)\n```\n'
                '`[inline sample](also-missing.md)`\n'
                '[Real reference][ref]\n\n[ref]: real%20file.md\n')
            self.assertEqual(bundles.check(root), [])
            with (skill / "SKILL.md").open("a") as file:
                file.write('\n[Broken](missing.md)\n[Outside](../../outside.md)\n')
            errors = bundles.check(root)
            self.assertEqual(len(errors), 2)
            self.assertTrue(any("missing.md" in error for error in errors))
            self.assertTrue(any("outside.md" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
