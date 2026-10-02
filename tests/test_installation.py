import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("reflection-weaver", "signal-detector", "strategic-reading", "quality-review", "citation-fixer")


def files(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class InstallationTests(unittest.TestCase):
    def install(self, workspace):
        return subprocess.run(["sh", str(ROOT / "scripts/install-manual.sh"), str(workspace)],
                              capture_output=True, text=True)

    def test_copy_full_bundles_and_preserve_unrelated_skill(self):
        with tempfile.TemporaryDirectory(prefix="pack test ") as tmp:
            workspace = Path(tmp) / "chosen workspace"
            unrelated = workspace / "skills/unrelated/SKILL.md"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text("user owned")
            self.assertEqual(self.install(workspace).returncode, 0)
            pack = workspace / "skills/jjjhenriksen-pack"
            for name in NAMES:
                self.assertEqual(files(pack / name), files(ROOT / name))
            before = files(workspace)
            self.assertNotEqual(self.install(workspace).returncode, 0)
            self.assertEqual(files(workspace), before)
            # Removal is a move outside every discovery root, preserving edits.
            (pack / "signal-detector/local-note.md").write_text("user addition")
            pack.rename(Path(tmp) / "removed-pack")
            self.assertFalse(pack.exists())
            self.assertEqual(unrelated.read_text(), "user owned")
            self.assertEqual((Path(tmp) / "removed-pack/signal-detector/local-note.md").read_text(), "user addition")

    def test_existing_file_and_symlink_are_not_overwritten(self):
        for kind in ("file", "symlink", "dangling symlink", "directory"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                workspace = Path(tmp) / "workspace"
                skills = workspace / "skills"
                skills.mkdir(parents=True)
                destination = skills / "jjjhenriksen-pack"
                if kind == "file":
                    destination.write_text("existing")
                elif kind == "directory":
                    destination.mkdir()
                else:
                    target = Path(tmp) / "elsewhere"
                    if kind == "symlink":
                        target.mkdir()
                        (target / "keep.md").write_text("untouched")
                    destination.symlink_to(target, target_is_directory=True)
                before = files(Path(tmp))
                self.assertNotEqual(self.install(workspace).returncode, 0)
                self.assertEqual(files(Path(tmp)), before)
                if "symlink" in kind:
                    self.assertTrue(destination.is_symlink())

    def test_relative_destination_rejected(self):
        self.assertNotEqual(self.install("relative/workspace").returncode, 0)


if __name__ == "__main__":
    unittest.main()
