import time

import win32api

from ok import find_boxes_by_name, Logger, calculate_color_percentage
from ok import find_color_rectangles, get_mask_in_color_range, is_pure_black
from src.Labels import Labels
from src.tasks.BaseNTETask import BaseNTETask

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.char.BaseChar import BaseChar

logger = Logger.get_logger(__name__)


class CombatCheck(BaseNTETask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._in_combat = False
        self.skip_combat_check = False
        self.sleep_check_interval = 0.4
        self.last_out_of_combat_time = 0
        self.out_of_combat_reason = ""
        self.target_enemy_time_out = 3
        self.switch_char_time_out = 5
        self.combat_end_condition = None
        self.target_enemy_error_notified = False
        self.cds = {
        }

    @property
    def in_ultimate(self):
        return self._in_ultimate

    @in_ultimate.setter
    def in_ultimate(self, value):
        self._in_ultimate = value
        if value:
            self._last_ultimate = time.time()

    def on_combat_check(self):
        return True

    def reset_to_false(self, reason=""):
        self.out_of_combat_reason = reason
        self.do_reset_to_false()
        return False

    def do_reset_to_false(self):
        self.cds = {}
        self._in_combat = False
        self.scene.set_not_in_combat()
        return False

    def get_current_char(self) -> 'BaseChar':
        """
        获取当前角色。
        此方法必须由子类实现。
        """
        raise NotImplementedError("子类必须实现 get_current_char 方法")

    def load_chars(self) -> bool:
        """
        加载队伍中的角色信息。
        此方法必须由子类实现。
        """
        raise NotImplementedError("子类必须实现 load_chars 方法")

    def check_health_bar(self):
        return self.has_health_bar() or self.is_boss()

    def is_boss(self):
        # return self.find_one('boss_break_shield') or self.find_one('boss_break_lock')
        return False

    def has_health_bar(self):
        if self._in_combat:
            min_height = self.height_of_screen(9 / 2160)
            max_height = min_height * 3
            min_width = self.width_of_screen(12 / 3840)
        else:
            min_height = self.height_of_screen(7 / 2160)
            max_height = min_height * 3
            min_width = self.width_of_screen(100 / 3840)

        boxes = find_color_rectangles(self.frame, enemy_health_color_red, min_width, min_height, max_height=max_height)

        if len(boxes) > 0:
            self.draw_boxes('enemy_health_bar_red', boxes, color='blue')
            return True
        else:
            boxes = find_color_rectangles(self.frame, boss_health_color, min_width, min_height * 1.3,
                                          box=self.box_of_screen(0.3277, 0.0507, 0.4980, 0.0701))
            if len(boxes) == 1:
                self.boss_health_box = boxes[0]
                self.boss_health_box.width = 10
                self.boss_health_box.x += 6
                self.boss_health = self.boss_health_box.crop_frame(self.frame)
                self.draw_boxes('boss_health', boxes, color='blue')
                return True
        return False

    def in_combat(self, target=False):
        self.in_sleep_check = True
        try:
            return self.do_check_in_combat(target)
        except Exception as e:
            logger.error(f'do_check_in_combat: {e}')
        finally:
            self.in_sleep_check = False

    def do_check_in_combat(self, target):
        if self.in_ultimate:
            return True
        if self._in_combat:
            if self.scene.in_combat() is not None:
                return self.scene.in_combat()
            if current_char := self.get_current_char():
                if current_char.skip_combat_check():
                    return self.scene.set_in_combat()
            if not self.on_combat_check():
                self.log_info('on_combat_check failed')
                return self.reset_to_false(reason='on_combat_check failed')
            # if self.has_target():
            #     self.last_in_realm_not_combat = 0
            #     return self.scene.set_in_combat()
            if self.combat_end_condition is not None and self.combat_end_condition():
                return self.reset_to_false(reason='end condition reached')
            # if self.target_enemy(wait=True):
            #     logger.debug('retarget enemy succeeded')
            #     return self.scene.set_in_combat()
            # if self.should_check_monthly_card() and self.handle_monthly_card():
            #     return self.scene.set_in_combat()
            logger.error('target_enemy failed, try recheck break out of combat')
            return self.reset_to_false(reason='target enemy failed')
        else:
            in_combat = self.check_health_bar()
            if in_combat:
                self.log_info('enter combat')
                self._in_combat = self.load_chars()
                return self._in_combat


enemy_health_color_red = {
    "r": (215, 255),  # Red range
    "g": (40, 70),  # Green range
    "b": (20, 55),  # Blue range
}

boss_health_color = {
    "r": (235, 255),  # Red range
    "g": (50, 95),  # Green range
    "b": (40, 75),  # Blue range
}