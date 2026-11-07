import unittest
from unittest.mock import Mock

from src.tasks.mixin.OgMixin import OgMixin


class SaveableConfig:
    def __init__(self):
        self.save_file = Mock()


class TestOgMixin(unittest.TestCase):
    def test_sync_config_saves_target_and_refreshes_its_ui(self):
        task = object.__new__(OgMixin)
        config = SaveableConfig()
        task._refresh_config_ui = Mock()

        task.sync_config(config)

        config.save_file.assert_called_once_with()
        task._refresh_config_ui.assert_called_once_with(config)

    def test_sync_config_uses_task_config_by_default(self):
        task = object.__new__(OgMixin)
        task.config = {}
        task._refresh_config_ui = Mock()

        task.sync_config()

        task._refresh_config_ui.assert_called_once_with(task.config)


if __name__ == "__main__":
    unittest.main()
