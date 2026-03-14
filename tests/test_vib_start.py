import unittest

from vibelign.commands.vib_start_cmd import _next_step, _status_line


class VibStartTest(unittest.TestCase):
    def test_status_line_uses_simple_language(self):
        self.assertIn("좋아요", _status_line("Good"))
        self.assertIn("문제를 확인", _status_line("High Risk"))

    def test_next_step_uses_first_recommended_action(self):
        data = {
            "recommended_actions": ["vib anchor --suggest", "vib doctor --detailed"]
        }
        self.assertEqual(_next_step(data), "vib anchor --suggest")


if __name__ == "__main__":
    unittest.main()
