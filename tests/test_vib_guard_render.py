import unittest
import importlib


_render_markdown = importlib.import_module(
    "vibeguard.commands.vib_guard_cmd"
)._render_markdown


class VibGuardRenderTest(unittest.TestCase):
    def test_render_markdown_contains_status_and_next_steps(self):
        markdown = _render_markdown(
            {
                "status": "warn",
                "strict": False,
                "project_score": 68,
                "project_status": "Caution",
                "change_risk_level": "MEDIUM",
                "summary": "구조 위험이 조금 있습니다.",
                "recommendations": ["vib anchor --suggest", "vib guard --strict"],
                "protected_violations": [],
                "explain": {
                    "files": [{"path": "app.py", "status": "modified", "kind": "logic"}]
                },
            }
        )
        self.assertIn("Status: warn", markdown)
        self.assertIn("## Recommended next steps", markdown)
        self.assertIn("`app.py`", markdown)


if __name__ == "__main__":
    unittest.main()
