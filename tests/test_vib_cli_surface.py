import unittest
from typing import Any, cast

from vibeguard.vib_cli import build_parser


class VibCliSurfaceTest(unittest.TestCase):
    def test_vib_cli_includes_remaining_legacy_commands(self):
        parser = build_parser()
        subparsers_action = cast(
            Any,
            next(
                action for action in parser._actions if getattr(action, "choices", None)
            ),
        )
        commands = set(subparsers_action.choices.keys())
        self.assertTrue(
            {"protect", "ask", "config", "export", "watch"}.issubset(commands)
        )


if __name__ == "__main__":
    unittest.main()
