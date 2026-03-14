import io
import importlib
import importlib.util
import unittest
from contextlib import redirect_stdout

from vibelign.terminal_render import normalize_ai_output, print_ai_response


class TerminalRenderTests(unittest.TestCase):
    def test_normalize_keeps_code_fence_content(self) -> None:
        text = """### 제목

\u2022 첫 항목
1) 둘째 항목

```py
\u2022 keep
1) keep
```
"""

        normalized = normalize_ai_output(text)

        self.assertIn("- 첫 항목", normalized)
        self.assertIn("1. 둘째 항목", normalized)
        self.assertIn("\u2022 keep", normalized)
        self.assertIn("1) keep", normalized)

    def test_normalize_preserves_blank_lines_inside_code_fence(self) -> None:
        text = """```python
print('a')


print('b')
```"""

        normalized = normalize_ai_output(text)

        self.assertIn("print('a')\n\n\nprint('b')", normalized)

    def test_plain_render_falls_back_without_rich(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_ai_response("### 제목\n\n- 항목", use_rich=False)

        self.assertIn("### 제목", buffer.getvalue())
        self.assertIn("- 항목", buffer.getvalue())

    def test_rich_render_converts_sections_without_raw_markdown(self) -> None:
        console_mod = importlib.util.find_spec("rich.console")
        if console_mod is None:
            self.skipTest("rich is not installed")

        Console = importlib.import_module("rich.console").Console
        console = Console(record=True, width=80)
        print_ai_response(
            "## 1. 한 줄 요약\n이 파일은 로그인 흐름을 처리합니다.\n\n## 2. 주요 기능을 쉬운 말로 설명\n- 인증 확인\n- 토큰 발급",
            console=console,
            use_rich=True,
        )
        rendered = console.export_text()

        self.assertIn("1. 한 줄 요약", rendered)
        self.assertIn("- 인증 확인", rendered)
        self.assertNotIn("## 1. 한 줄 요약", rendered)


if __name__ == "__main__":
    unittest.main()
