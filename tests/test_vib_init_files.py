import tempfile
import unittest
from pathlib import Path

from vibelign.commands.vib_init_cmd import _ensure_core_rule_files


class VibInitFilesTest(unittest.TestCase):
    def test_init_creates_core_rule_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _ensure_core_rule_files(root)
            self.assertTrue((root / "AI_DEV_SYSTEM_SINGLE_FILE.md").exists())
            self.assertTrue((root / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
