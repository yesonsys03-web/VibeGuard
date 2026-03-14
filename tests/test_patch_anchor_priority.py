import json
import tempfile
import unittest
from pathlib import Path

from vibelign.core.patch_suggester import suggest_patch


class PatchAnchorPriorityTest(unittest.TestCase):
    def test_real_anchor_match_beats_better_path_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "login_panel_render.py").write_text(
                "def helper():\n    return True\n", encoding="utf-8"
            )
            (root / "login_service.py").write_text(
                "# === ANCHOR: LOGIN_SERVICE_START ===\n# === ANCHOR: LOGIN_PANEL_START ===\ndef login_panel():\n    return True\n# === ANCHOR: LOGIN_PANEL_END ===\n# === ANCHOR: LOGIN_SERVICE_END ===\n",
                encoding="utf-8",
            )
            meta_dir = root / ".vibelign"
            meta_dir.mkdir()
            (meta_dir / "anchor_index.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "anchors": {
                            "login_service.py": ["LOGIN_SERVICE", "LOGIN_PANEL"],
                        },
                        "files": {
                            "login_service.py": {
                                "anchors": ["LOGIN_SERVICE", "LOGIN_PANEL"],
                                "suggested_anchors": ["LOGIN_PANEL"],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = suggest_patch(root, "login panel")
            self.assertEqual(result.target_file, "login_service.py")
            self.assertEqual(result.target_anchor, "LOGIN_PANEL")
            self.assertTrue(
                any("실제 앵커 'LOGIN_PANEL'" in item for item in result.rationale),
                result.rationale,
            )


if __name__ == "__main__":
    unittest.main()
