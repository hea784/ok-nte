import time

from qfluentwidgets import FluentIcon

from ok import TaskDisabledException
from src.combat.BaseCombatTask import BaseCombatTask
from src.sound_trigger.SoundCombatContext import SoundCombatContext
from src.tasks.NTEOneTimeTask import NTEOneTimeTask


class WhirlwindTask(NTEOneTimeTask, BaseCombatTask):
    TARGET_NAVIGATION_ANGLE = -154.5
    NAVIGATION_ANGLE_TOLERANCE = 5
    NAVIGATION_FAILED_TIMEOUT = 4
    NAVIGATION_FAILED_RETRY_INTERVAL = 0.25
    NAVIGATION_CONFIRM_DELAY = 0.5
    CONFIG_DIFF_OPTION = "难度选项"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动小旋风"
        self.description = "可交互「小旋风」下按开始"
        self.icon = FluentIcon.FLAG
        self.group_name = "都市闲趣"
        self.default_config.update(
            {
                self.CONFIG_DIFF_OPTION: 1,
            }
        )

    def run(self):
        super().run()
        try:
            self.do_run()
        except TaskDisabledException:
            pass
        except Exception as e:
            self.log_error("WhirlwindTask Error", e)

    def do_run(self):
        SoundCombatContext().update_task(self, dodge_action=self._dodge_with_skill)
        try:
            while True:
                if not self.is_boss():
                    if not self.find_interac():
                        self.navigate()
                        self.sleep(0.1)
                    self.start_interac()
                self.start_combat()
        finally:
            self._release_navigation_keys()

    def _dodge_with_skill(self):
        self.send_key(self.get_skill_key())

    def start_interac(self):
        self.send_key("f", after_sleep=0.5)
        self.send_key_down("w")
        self.wait_until(
            lambda: not self.is_in_team(),
            pre_action=lambda: self.send_key("f", interval=0.25),
            time_out=20,
        )
        self.send_key_up("w")

        diff_option = self.config.get(self.CONFIG_DIFF_OPTION, 1)
        ratio_x = 0.701
        ratio_y = 0.542 + 0.068 * (diff_option - 1)

        self.wait_until(
            self.is_in_team,
            pre_action=lambda: self.operate_click(ratio_x, ratio_y, interval=2),
            settle_time=1,
            time_out=60,
        )

    def start_combat(self):
        if not self.is_boss():
            self.send_key_down("w")
            self.sleep(0.2)
            self.send_key("lshift")
            self.wait_until(self.is_boss)
            self.send_key_up("w")
        with self.skip_sleep_checks() as skip:
            skip.check_combat = True
            self.sleep(4)
            while True:
                self.click()
                self.sleep(0.15)
                self.send_key(self.get_ultimate_key())
                self.sleep(0.15)
                if not self.is_boss() and self.is_in_team():
                    break
        self.sleep(2)
        self.wait_in_team(time_out=60, settle_time=1)
        self.click(key="middle")
        self.sleep(1)

    def navigate(self):
        self.wait_in_team()
        self.send_key("lctrl", after_sleep=0.25)
        failed_start = None
        try:
            while True:
                angle = self._navigation_angle()
                if angle is None:
                    if failed_start is None:
                        failed_start = time.time()
                    elif time.time() - failed_start > self.NAVIGATION_FAILED_TIMEOUT:
                        return False
                    self.sleep(self.NAVIGATION_FAILED_RETRY_INTERVAL)
                    continue
                failed_start = None

                error = self._normalize_angle(self.TARGET_NAVIGATION_ANGLE - angle)
                if abs(error) <= self.NAVIGATION_ANGLE_TOLERANCE:
                    if self._confirm_navigation_angle():
                        return True
                    continue

                self._fine_tune_navigation(self._navigation_side_key(angle), abs(error), angle)
        finally:
            self._release_navigation_keys()

    def _navigation_angle(self):
        ret = self.check_mini_map_arrow()
        if not ret:
            return None
        return ret[0].get("angle")

    def _confirm_navigation_angle(self):
        self.sleep(self.NAVIGATION_CONFIRM_DELAY)
        self.send_key("w")

        angle = self._navigation_angle()
        if angle is None:
            return False

        error = self._normalize_angle(self.TARGET_NAVIGATION_ANGLE - angle)
        return abs(error) <= self.NAVIGATION_ANGLE_TOLERANCE

    def _navigation_side_key(self, current_angle):
        error = self._normalize_angle(self.TARGET_NAVIGATION_ANGLE - current_angle)
        return "d" if error < 0 else "a"

    def _fine_tune_navigation(self, side_key, angle_diff, current_angle):
        turn_key = self._best_navigation_turn_key(current_angle, side_key)
        if turn_key is not None:
            self.send_key(turn_key)
            self.sleep(0.5)
        else:
            try:
                self.send_key_down(side_key)
                self.send_key("w")
            finally:
                self.send_key_up(side_key)
            self.sleep(0.05)

        self.click(key="middle")
        self.sleep(0.75)
        self.send_key("w")
        self.sleep(0.5)
        self.next_frame()

    def _best_navigation_turn_key(self, current_angle, side_key):
        current_diff = abs(self._normalize_angle(self.TARGET_NAVIGATION_ANGLE - current_angle))

        side_angle_offset = -90 if side_key == "d" else 90
        side_turn_angle = self._normalize_angle(current_angle + side_angle_offset)
        turn_around_angle = self._normalize_angle(current_angle + 180)

        side_turn_diff = abs(self._normalize_angle(self.TARGET_NAVIGATION_ANGLE - side_turn_angle))
        turn_around_diff = abs(
            self._normalize_angle(self.TARGET_NAVIGATION_ANGLE - turn_around_angle)
        )
        if side_turn_diff >= current_diff and turn_around_diff >= current_diff:
            return None
        return "s" if turn_around_diff < side_turn_diff else side_key

    def _release_navigation_keys(self):
        self.send_key("lctrl")
        self.send_key_up("a")
        self.send_key_up("d")
