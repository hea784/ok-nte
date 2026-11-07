import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.ui.task_icons import Icon


class TestTaskIcons(unittest.TestCase):
    def tearDown(self):
        Icon.configure("web")

    def test_web_mode_uses_serializable_names(self):
        Icon.configure("web")

        self.assertEqual(Icon.CALENDAR, "calendar")
        self.assertEqual(Icon.GAME, "game")

    def test_qt_mode_lazily_uses_fluent_icons(self):
        calendar_icon = object()
        game_icon = object()
        module = SimpleNamespace(FluentIcon=SimpleNamespace(CALENDAR=calendar_icon, GAME=game_icon))

        with patch.dict(sys.modules, {"qfluentwidgets": module}):
            Icon.configure("qt")

        self.assertIs(Icon.CALENDAR, calendar_icon)
        self.assertIs(Icon.GAME, game_icon)

    def test_unknown_mode_leaves_icons_unchanged(self):
        Icon.configure("web")

        Icon.configure(None)

        self.assertEqual(Icon.CALENDAR, "calendar")
        self.assertEqual(Icon.GAME, "game")


if __name__ == "__main__":
    unittest.main()
