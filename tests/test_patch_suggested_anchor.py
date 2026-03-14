import json
import tempfile
import unittest
from pathlib import Path

from vibelign.core.patch_suggester import suggest_patch


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

    def test_patch_does_not_use_weak_unmatched_suggested_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "terminal_render.py"
            src.write_text("def helper():\n    return True\n", encoding="utf-8")
            meta_dir = root / ".vibelign"
            meta_dir.mkdir()
            (meta_dir / "anchor_index.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "anchors": {},
                        "files": {
                            "terminal_render.py": {
                                "anchors": [],
                                "suggested_anchors": ["_LOAD_RICH", "BUILD_PANEL"],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = suggest_patch(root, "login panel")
            self.assertEqual(result.target_anchor, "[먼저 앵커를 추가하세요]")

    def test_weak_suggested_anchor_does_not_boost_file_ranking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "login_notes.py").write_text(
                "def helper():\n    return True\n", encoding="utf-8"
            )
            (root / "terminal_render.py").write_text(
                "def helper():\n    return True\n", encoding="utf-8"
            )
            meta_dir = root / ".vibelign"
            meta_dir.mkdir()
            (meta_dir / "anchor_index.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "anchors": {},
                        "files": {
                            "terminal_render.py": {
                                "anchors": [],
                                "suggested_anchors": ["_LOAD_RICH", "BUILD_PANEL"],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = suggest_patch(root, "login panel")
            self.assertEqual(result.target_file, "login_notes.py")


if __name__ == "__main__":
    unittest.main()
