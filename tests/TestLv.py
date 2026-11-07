import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np
from ok.test.TaskTestCase import TaskTestCase

from src.combat.CombatCheck import CombatCheck
from src.config import config
from src.utils.visual_template_cache import reset_visual_template_cache_for_tests


class TestableCombatCheck(CombatCheck):
    @property
    def width(self):
        return 2560

    @property
    def height(self):
        return 1440


class TestOcrLv(TaskTestCase):
    task_class = CombatCheck

    config = config

    def test_enemy_lv_text(self):
        # Create a BattleReport object
        self.set_image('tests/images/03.png')
        result = self.task.find_lv()
        self.logger.info(f'enemy_lv_text: {result}')
        self.assertEqual(len(result), 2)

    def test_boss_lv_text(self):
        self.set_image('tests/images/04.png')
        result = self.task.is_boss()
        self.logger.info(f'test test_boss_lv_text: {result}')
        self.assertEqual(result, True)


class TestLvTemplateCache(unittest.TestCase):
    def setUp(self):
        reset_visual_template_cache_for_tests()

    def tearDown(self):
        reset_visual_template_cache_for_tests()

    @staticmethod
    def _make_task(template):
        task = object.__new__(TestableCombatCheck)
        task.get_feature_by_name = Mock(return_value=SimpleNamespace(mat=template))
        task.log_error = Mock()
        task.log_info = Mock()
        return task

    def test_two_task_instances_share_one_lv_template_initialization(self):
        template = np.zeros((40, 80), dtype=np.uint8)
        template[5:30, 5:10] = 255
        template[25:30, 5:22] = 255
        template[5:30, 40:45] = 255
        template[25:30, 45:57] = 255

        first_task = self._make_task(template)
        second_task = self._make_task(template)
        with patch("src.combat.CombatCheck.gf.isolate_lv_to_white", return_value=template):
            first_features = first_task._get_lv_template_features()
            second_features = second_task._get_lv_template_features()

        self.assertIsNotNone(first_features)
        self.assertIs(first_features, second_features)
        first_task.get_feature_by_name.assert_called_once()
        second_task.get_feature_by_name.assert_not_called()

if __name__ == '__main__':
    unittest.main()
