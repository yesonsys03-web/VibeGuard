import json
import tempfile
import unittest
from pathlib import Path

from vibeguard.core.patch_suggester import suggest_patch


class PatchSuggestedAnchorTest(unittest.TestCase):
    def test_patch_uses_suggested_anchor_when_real_anchor_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "login_ui.py"
            src.write_text(
                "def render_progress_bar():\n    return True\n", encoding="utf-8"
            )
            meta_dir = root / ".vibelign"
            meta_dir.mkdir()
            (meta_dir / "anchor_index.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "anchors": {},
                        "files": {
                            "login_ui.py": {
                                "anchors": [],
                                "suggested_anchors": ["RENDER_PROGRESS_BAR"],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = suggest_patch(root, "add progress bar")
            self.assertEqual(result.target_anchor, "[추천 앵커: RENDER_PROGRESS_BAR]")


if __name__ == "__main__":
    unittest.main()
