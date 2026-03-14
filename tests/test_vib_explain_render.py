import unittest

from vibeguard.commands.vib_explain_cmd import _render_markdown


class VibExplainRenderTest(unittest.TestCase):
    def test_render_markdown_uses_three_section_structure(self):
        markdown = _render_markdown(
            {
                "source": "git",
                "risk_level": "LOW",
                "what_changed": ["login.py 수정"],
                "why_it_matters": ["로그인 흐름이 달라질 수 있습니다."],
                "what_to_do_next": "다음으로 vib guard 를 실행하세요.",
                "files": [{"path": "login.py", "status": "modified", "kind": "logic"}],
                "summary": "최근 파일 변경이 있습니다.",
            }
        )
        self.assertIn("## 1. 한 줄 요약", markdown)
        self.assertIn("## 2. 변경된 내용", markdown)
        self.assertIn("## 3. 왜 중요한가", markdown)
        self.assertIn("## 4. 다음 할 일", markdown)


if __name__ == "__main__":
    unittest.main()
