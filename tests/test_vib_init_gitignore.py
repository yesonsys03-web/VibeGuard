import tempfile
import unittest
from pathlib import Path

from vibelign.commands.vib_init_cmd import _ensure_gitignore_entry


class VibInitGitignoreTest(unittest.TestCase):
    def test_init_ensures_checkpoints_gitignore_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _ensure_gitignore_entry(root)
            text = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".vibelign/checkpoints/", text)


if __name__ == "__main__":
    unittest.main()
