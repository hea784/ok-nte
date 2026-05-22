import re
import time
from dataclasses import dataclass
from threading import Event

from ok import TaskDisabledException
from qfluentwidgets import FluentIcon

from src import text_white_color
from src.combat.BaseCombatTask import BaseCombatTask
from src.heist_path.HeistPathA import HeistPathA
from src.Labels import Labels
from src.tasks.NTEOneTimeTask import NTEOneTimeTask
from src.tasks.trigger.SkipDialogTask import SkipDialogTask
from src.utils import game_filters as gf
from src.utils import image_utils as iu


class AbortException(Exception):
    pass


@dataclass
class CharacterSwitchState:
    role: str
    keys: list[str]
    index: int = 0
    deadline: float = 0

    @property
    def current_key(self):
        return self.keys[self.index]

    def advance(self):
        self.index += 1
        return self.index < len(self.keys)


INST = r"""
        <span style="color:red;">
            <strong>站在可互动小吱的位置开始</strong>
        </span>
        <div style="color:white;">
            <strong>路径1推荐设置</strong>
            <div style="margin-left:2em;">战斗角色: 主角 / 娜娜莉</div>
            <div style="margin-left:2em;">跑图角色: 薄荷</div>
            <div style="margin-left:2em;">避战角色(可选): 翳 / 浔</div>
        </div>
    """


class AutoHeistTask(NTEOneTimeTask, BaseCombatTask):
    CONF_LOOP_COUNT = "循环次数"
    CONF_PATH = "路径"
    CONF_FIGHTER = "战斗角色"
    CONF_RUNNER = "跑图角色"
    CONF_AVOIDER = "避战角色"
    CONF_AVOID_MTH = "避战方法"
    ROLE_FIGHTER = "fighter"
    ROLE_RUNNER = "runner"
    ROLE_AVOIDER = "avoider"
    AVOID_METHOD_DASH = "长按shift"
    AVOID_METHOD_ATTACK = "长按攻击"
    LOCK_PICK_MATCH_THRESHOLD = 0.75
    SLEEP_CHECK_INTERVAL = 0.1
    SWITCH_CHECK_DURATION = 3
    QUICK_PICK_START_DELAY = 0.3
    QUICK_PICK_INTERVAL = 0.2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动粉爪大劫案"
        self.icon = FluentIcon.SHOPPING_CART
        self.instructions = INST
        self.paths = {
            "路径1": HeistPathA,
        }
        path_names = list(self.paths.keys())
        self.avoid_methods = [self.AVOID_METHOD_DASH, self.AVOID_METHOD_ATTACK]
        self.default_config.update(
            {
                self.CONF_LOOP_COUNT: 0,
                self.CONF_PATH: path_names[0],
                self.CONF_FIGHTER: ["4", "1"],
                self.CONF_RUNNER: ["3"],
                self.CONF_AVOIDER: ["2"],
                self.CONF_AVOID_MTH: self.AVOID_METHOD_DASH,
            }
        )
        self.config_description.update(
            {
                self.CONF_LOOP_COUNT: "循环次数, 设置为0则一直运行",
                self.CONF_FIGHTER: "选1~2个",
                self.CONF_RUNNER: "选1个",
                self.CONF_AVOIDER: "选0~1个",
            }
        )

        options = ["1", "2", "3", "4"]
        self.config_type.update(
            {
                self.CONF_PATH: {
                    "type": "drop_down",
                    "options": path_names,
                },
                self.CONF_AVOID_MTH: {
                    "type": "drop_down",
                    "options": self.avoid_methods,
                },
                self.CONF_FIGHTER: {"type": "multi_selection", "options": options},
                self.CONF_RUNNER: {"type": "multi_selection", "options": options},
                self.CONF_AVOIDER: {"type": "multi_selection", "options": options},
            }
        )
        self.sleep_check_interval = self.SLEEP_CHECK_INTERVAL
        self._scroll_switch = False
        self._scroll_count = 0
        self._scroll_time = 0
        self._dead_fighter_keys = []
        self._current_fighter_key = None
        self._switch_state: CharacterSwitchState | None = None
        self._handling_switch_state = False
        self._quick_pick_event = Event()
        self._quick_pick_ready_at = 0
        self._held_keys = set()
        self._interaction_watch_active = False
        self._interaction_watch_found = False

        self._round_label = ""
        self._error_count = 0

    def run(self):
        super().run()
        try:
            return self._run_loop()
        except TaskDisabledException:
            pass
        except Exception as e:
            self.log_error("自动粉爪大劫案出错", e)
            raise

    def _run_loop(self):
        self._start_quick_pick_loop()
        self._round_label = ""
        self._error_count = 0
        self.info_set("总方斯获取数", 0)
        self.info_set("总粉爪币获取数", 0)

        count = 0

        total = int(self.config.get(self.CONF_LOOP_COUNT, 1))
        endless = total == 0
        skip_task = self.get_task_by_class(SkipDialogTask)
        while endless or count < total:
            count += 1
            self._prepare_round(count, total, endless)

            rewards = self._run_heist_round(skip_task)
            if rewards is not None:
                self._add_rewards_to_summary(*rewards)

            self.next_frame()

    def _start_quick_pick_loop(self):
        self.log_info("quick_pick_loop start")
        self.submit_periodic_task(0.01, self._quick_pick_loop)

    def _prepare_round(self, count, total, endless):
        self._dead_fighter_keys = []
        self._round_label = f"第 {count} 轮"
        round_text = "∞" if endless else f"{total}"

        self.info_set("轮次", f"{count} / {round_text}")
        self.info_set("失败次数", self._error_count)

    def _add_rewards_to_summary(self, earnfcash, earnpcoin):
        self.info_add("总方斯获取数", earnfcash)
        self.info_add("总粉爪币获取数", earnpcoin)

    def _run_heist_round(self, skip_task):
        if not self.wait_until(self.find_interac, time_out=20, raise_if_not_found=True):
            return None

        self.enter_heist()
        if not self._wait_until_heist_loaded(skip_task):
            self.abort_heist()
            return None

        try:
            self.run_path()
        except AbortException as e:
            self.log_warning(e)
            self.abort_heist()
            return None

        return self.exit_heist()

    def _wait_until_heist_loaded(self, skip_task):
        return self.wait_until(
            self.in_heist,
            post_action=lambda: skip_task.check_skip(),
            time_out=600,
            settle_time=1,
        )

    def sleep_check(self):
        self._poll_interaction_watch()
        self._poll_character_switch()
        if self.should_check_monthly_card():
            if self.handle_monthly_card():
                raise AbortException("found monthly_card")

    def start_interaction_watch(self):
        self.sleep_check_interval = self.SLEEP_CHECK_INTERVAL
        self._interaction_watch_active = True
        self._interaction_watch_found = False
        self.info_set("交互检查", "检查中")
        self.log_info("start interaction watch")

    def stop_interaction_watch(self):
        if not self._interaction_watch_active and not self._interaction_watch_found:
            self.log_warning("stop interaction watch ignored: not started")
            return True

        found = self._interaction_watch_found
        self.sleep_check_interval = self.SLEEP_CHECK_INTERVAL
        self._interaction_watch_active = False
        self._interaction_watch_found = False
        self.info_set("交互检查", None)

        if not found:
            raise AbortException("not found interac")
        return True

    def _poll_interaction_watch(self):
        if not self._interaction_watch_active or self._interaction_watch_found:
            return self._interaction_watch_found
        if self.find_interac():
            self._interaction_watch_found = True
            self._interaction_watch_active = False
            self.info_set("交互检查", "已找到")
            self.log_info("interaction watch succeeded")
        return self._interaction_watch_found

    def _begin_character_switch(self, role, keys):
        if not keys:
            raise AbortException(f"{role} {keys} dead or empty")

        self._switch_state = CharacterSwitchState(role=role, keys=keys)
        return self._send_current_switch_key()

    def _send_current_switch_key(self):
        state = self._switch_state
        if state is None:
            return None
        key = state.current_key
        if state.role == self.ROLE_FIGHTER:
            self._current_fighter_key = key
        state.deadline = time.time() + self.SWITCH_CHECK_DURATION
        self.send_key(key)
        return key

    def _poll_character_switch(self):
        if self._switch_state is None or self._handling_switch_state:
            return

        state = self._switch_state
        if time.time() > state.deadline:
            self._switch_state = None
            return

        if self.is_in_team():
            return

        self._handling_switch_state = True
        try:
            role = state.role
            key = state.current_key
            self.log_info(f"{role} char {key} is dead")
            if role == self.ROLE_FIGHTER and key not in self._dead_fighter_keys:
                self._dead_fighter_keys.append(key)
            self.ensure_in_team()

            if not state.advance():
                self._switch_state = None
                raise AbortException(f"{role} {state.keys} dead or empty")
            self._send_current_switch_key()
        finally:
            self._handling_switch_state = False

    def handle_monthly_card(self):
        monthly_card = self.find_monthly_card()
        # self.screenshot('monthly_card1')
        if monthly_card is not None:
            # self.screenshot('monthly_card1')
            self.log_info("monthly_card found click")
            self.click(0.50, 0.89)
            self.sleep(2)
            # self.screenshot('monthly_card2')
            self.click(0.50, 0.89)
            self.sleep(2)
            self.wait_until(
                self.in_team,
                time_out=10,
                post_action=lambda: self.click(0.50, 0.89, after_sleep=1),
            )
            # self.screenshot('monthly_card3')
            self.set_check_monthly_card(next_day=True)
        # logger.debug(f'check_monthly_card {monthly_card}')
        return monthly_card is not None

    def log_round_info(self, message):
        self.log_info(f"{self._round_label}: {message}")

    def get_heist_rewards(self):
        cash = self.ocr(
            0.359, 0.595, 0.500, 0.642, frame_processor=gf.isolate_text_to_black, name="cash"
        )
        coin = self.ocr(
            0.654, 0.595, 0.789, 0.641, frame_processor=gf.isolate_text_to_black, name="coin"
        )
        return self._parse_reward_number(cash, "earnfcash"), self._parse_reward_number(
            coin, "earnpcoin"
        )

    def _parse_reward_number(self, ocr_result, log_name):
        if not ocr_result:
            return 0

        result = "".join(item.name for item in ocr_result)
        result = re.sub(r"[,.]", "", result)
        match = re.search(r"(\d+)", result)
        if not match:
            return 0

        try:
            return int(match.group(1))
        except ValueError:
            self.log_warning(f"{log_name} error {result}")
            return 0

    def abort_heist(self):
        self.log_round_info("出现异常，将退出粉爪副本")
        self._error_count += 1

        self.wait_until(
            lambda: (
                self.is_in_team_outside_heist()
                or self.ocr(0.46, 0.32, 0.54, 0.37, match=re.compile("确认退出"))
            ),
            pre_action=lambda: self.send_key("esc", action_name="quit_heist", interval=2),
            time_out=60,
            raise_if_not_found=True,
        )
        if self.is_in_team_outside_heist():
            self.log_round_info("当前已在队伍界面且不在粉爪副本中，跳过退出副本")
            return

        btn = self.wait_ocr(
            0.52, 0.63, 0.68, 0.68, match=re.compile("确认"), time_out=60, raise_if_not_found=True
        )
        self.wait_until(
            lambda: not self.ocr(0.46, 0.32, 0.54, 0.37, match=re.compile("确认退出")),
            pre_action=lambda: self.operate_click(btn, action_name="quit_heist", interval=1),
            time_out=60,
            raise_if_not_found=True,
        )
        self.wait_in_team(time_out=60)
        self.log_round_info("已退出粉爪副本")

    # 进入粉爪副本
    def enter_heist(self):
        skip_task = self.get_task_by_class(SkipDialogTask)

        def in_panel():
            return self.ocr(0.625, 0.483, 0.685, 0.525, match=re.compile("挑战时间"))

        def action():
            self.send_key("f", action_name="enter_heist_f", interval=1)
            if not self.is_in_team():
                self.sleep(0.1)
                skip_task.check_skip()

        self.wait_until(
            in_panel,
            pre_action=action,
            time_out=20,
        )
        self.sleep(0.5)
        self.wait_until(
            lambda: not in_panel(),
            pre_action=lambda: self.operate_click(0.7734, 0.8824, interval=1),
            time_out=20,
        )
        self.sleep(0.5)

    def has_extract_panel(self):
        return self.ocr(0.2602, 0.2639, 0.3520, 0.3257, match=re.compile("安全撤离"))

    def is_in_team_outside_heist(self):
        return self.is_in_team() and not self.in_heist()

    # 离开粉爪副本
    def exit_heist(self):

        def in_sum_panel():
            return self.ocr(0.4496, 0.8354, 0.5547, 0.8868, match=re.compile("退出"))

        self.wait_until(
            lambda: self.is_in_team_outside_heist() or self.has_extract_panel(),
            pre_action=lambda: self.send_key("f", interval=1),
        )
        if self.is_in_team_outside_heist():
            self.log_round_info("当前已在队伍界面且不在粉爪副本中，跳过离开副本")
            return 0, 0

        self.sleep(1)
        earnfcash, earnpcoin = self.get_heist_rewards()
        self.wait_until(
            lambda: not self.has_extract_panel(),
            pre_action=lambda: self.operate_click(0.604, 0.701, interval=1),
        )
        self.sleep(1)
        self.wait_until(
            in_sum_panel,
        )
        self.sleep(1)
        self.wait_until(
            lambda: not in_sum_panel(),
            pre_action=lambda: self.operate_click(0.501, 0.864, interval=1),
        )
        self.sleep(1)
        self.wait_in_team(time_out=600)
        self.log_round_info("已离开粉爪副本")
        return earnfcash, earnpcoin

    def send_key_down(self, key, after_sleep=0):
        if key == "f":
            self._start_quick_pick()
            self._scroll_switch = False
            return
        self._held_keys.add(key)
        return super().send_key_down(key, after_sleep)

    def send_key_up(self, key, after_sleep=0):
        if key == "f":
            self._reset_quick_pick()
            return
        try:
            return super().send_key_up(key, after_sleep)
        finally:
            self._held_keys.discard(key)

    def _reset_quick_pick(self):
        self._quick_pick_event.clear()
        self._quick_pick_ready_at = 0

    def _start_quick_pick(self):
        if not self._quick_pick_event.is_set():
            self._quick_pick_ready_at = time.time() + self.QUICK_PICK_START_DELAY
        self._quick_pick_event.set()

    def _release_held_keys(self):
        held_keys = list(self._held_keys)
        self._held_keys.clear()
        for key in held_keys:
            try:
                super().send_key_up(key)
            except Exception as e:
                self.log_error(f"release held key {key} failed", e)

    def _quick_pick_loop(self):
        if self._should_stop_quick_pick_loop():
            return False

        if self._quick_pick_event.is_set() and time.time() >= self._quick_pick_ready_at:
            if self.check_action_interval("quick_pick", self.QUICK_PICK_INTERVAL):
                interaction = self.executor.interaction
                if interaction is not None:
                    interaction.send_key("f", 0.002)
            time.sleep(0.001)
            if self._should_stop_quick_pick_loop():
                return False
            self._alternate_scroll(interval=self.QUICK_PICK_INTERVAL)

    def _should_stop_quick_pick_loop(self):
        if not self.enabled or not self.running:
            self.log_info("quick_pick_loop stop")
            return True
        return False

    def _alternate_scroll(self, interval=0):
        if time.time() - self._scroll_time >= interval:
            time.sleep(0.01)
            if self._should_stop_quick_pick_loop():
                return False
            interaction = self.executor.interaction
            if interaction is None:
                return False
            if self._scroll_switch:
                interaction.scroll(0, 0, 1)
            else:
                interaction.scroll(0, 0, -1)
            self._scroll_time = time.time()
            self._scroll_count += 1
            if self._scroll_count >= 3:
                self._scroll_count = 0
                self._scroll_switch = not self._scroll_switch

    def run_path(self):
        path_name = self.config.get(self.CONF_PATH)
        path_cls = self.paths.get(path_name, next(iter(self.paths.values())))
        path = path_cls(self)
        try:
            path.run_path()
        finally:
            self._release_held_keys()
            self._reset_quick_pick()
            if self._interaction_watch_active:
                self.stop_interaction_watch()

    def ensure_in_team(self):
        self.wait_until(self.is_in_team, pre_action=lambda: self.send_key("esc", interval=2))

    def check_current_floor(self, floor=1):
        """检查是否在指定楼层"""
        floor_str = "LG" + str(floor)
        ret = self.wait_ocr(0.04, 0.235, 0.11, 0.275, match=re.compile("LG.*"), time_out=10)
        if ret and floor_str in ret[0].name:
            return
        raise AbortException(f"not in floor {floor}")

    def in_heist(self):
        return self.is_in_team() and self.find_one(Labels.heist_timer)

    def switch_to_fighter(self):
        keys = list(self.config.get(self.CONF_FIGHTER, []))
        dead_keys = set(self._dead_fighter_keys)
        keys = [item for item in reversed(keys) if item not in dead_keys]
        return self._begin_character_switch(self.ROLE_FIGHTER, keys)

    def switch_to_runner(self):
        keys = self.config.get(self.CONF_RUNNER, [])
        self._begin_character_switch(self.ROLE_RUNNER, keys)

    def avoider_strategy_index(self):
        keys = self.config.get(self.CONF_AVOIDER, [])
        if not keys:
            return -1
        method_name = self.config.get(self.CONF_AVOID_MTH)
        if method_name not in self.avoid_methods:
            self.log_warning(f"unknown avoid method {method_name}, use {self.AVOID_METHOD_DASH}")
            return 0
        return self.avoid_methods.index(method_name)

    def switch_to_avoider(self):
        keys = self.config.get(self.CONF_AVOIDER, [])
        if not keys:
            self.log_info("no avoider")
            return
        self._begin_character_switch(self.ROLE_AVOIDER, keys)

    def perform_avoidance_action(self):
        method_name = self.config.get(self.CONF_AVOID_MTH)
        if method_name == self.AVOID_METHOD_DASH:
            self.send_key_down("w")
            self.sleep(0.1)
            self.send_key_down("lshift")
            self.sleep(1.0)
            self.send_key_up("lshift")
            self.sleep(0.1)
            self.send_key_up("w")
        elif method_name == self.AVOID_METHOD_ATTACK:
            self.click(down_time=0.6)

    def clear_current_combat(self):
        _key = self.switch_to_fighter()
        self.wait_until(self.has_health_bar)
        deadline = time.time() + 60
        settle = -1
        while time.time() < deadline:
            if settle < 0:
                self.send_key("space")
                self.sleep(0.25)
                self.click()
                self.sleep(0.4)
                if not self.is_in_team():
                    self.log_info(f"fighter {_key} dead, try next")
                    self._dead_fighter_keys.append(_key)
                    self.ensure_in_team()
                    _key = self.switch_to_fighter()
                else:
                    _key = self._current_fighter_key or _key
                self.send_key(_key)
                self.next_frame()
            else:
                self.sleep(0.1)
            if not self._find_red_health_bar(10):
                if settle < 0:
                    settle = time.time()
                if time.time() - settle > 2:
                    break
            else:
                settle = -1
        else:
            raise AbortException("timeout for clear_current_combat")
        self.switch_to_runner()

    def wait_and_interact(
        self, direction=None, interact=True, key_up_sleep=0.7, is_lock=False, time_out=10
    ):
        ret = self.wait_until(self.find_interac, time_out=time_out)
        if interact and direction is not None:
            self.send_key_up(direction)
            self.sleep(key_up_sleep)
        if not ret:
            raise AbortException("timeout for wait_and_interact")
        elif not interact:
            return True
        self.wait_until(
            lambda: not self.find_interac(), pre_action=lambda: self.send_key("f", interval=1)
        )
        if is_lock:
            self.wait_until(self.is_lock_pick_active, time_out=2)
            self.wait_until(lambda: not self.is_lock_pick_active(), settle_time=0.5)
            return not self.find_interac()
        return True

    def loot_safes_while_walking(self, direction=None, time_out=10, hold=False):
        deadline = time.time() + time_out
        if direction is not None:
            self.send_key_down(direction)
        while time.time() < deadline:
            if self.find_one(Labels.heist_interac_lock_pick, vertical_variance=0.05):
                lock_pick = time.time()
                if direction is not None:
                    self.send_key_up(direction)
                self.wait_until(self.is_lock_pick_active, settle_time=0.25)
                self.wait_until(lambda: not self.is_lock_pick_active(), settle_time=0.5)
                self.sleep(0.50)
                deadline += time.time() - lock_pick
                if direction is not None:
                    self.send_key_down(direction)
            self.next_frame()
        if direction is not None and not hold:
            self.send_key_up(direction)

    def wait_for_safe_loot(self, time_out=10, raise_timeout=False):
        deadline = time.time() + time_out
        while time.time() < deadline:
            if self.find_one(Labels.heist_interac_lock_pick, vertical_variance=0.05):
                self.wait_until(self.is_lock_pick_active)
            if self.is_lock_pick_active():
                self.wait_until(lambda: not self.is_lock_pick_active(), settle_time=0.5)
                self.sleep(0.50)
                break
            self.next_frame()
        else:
            if raise_timeout:
                raise AbortException("timeout for wait_for_safe_loot")

    def is_lock_pick_active(self):
        feature = self.get_feature_by_name(Labels.heist_lock_pick).mat
        box = self.get_box_by_name(Labels.heist_lock_pick).scale(1.5)
        self.draw_boxes(boxes=box, color="blue")
        cropped = box.crop_frame(self.frame)
        cropped = iu.create_color_mask(cropped, text_white_color)
        # iu.show_images([feature, cropped], ["feature", "cropped"])
        res, _ = self._find_rotated_template(
            feature,
            cropped,
            threshold=self.LOCK_PICK_MATCH_THRESHOLD,
            cache_key=Labels.heist_lock_pick,
        )
        return len(res) >= 1

    def try_open_exit(self, direction=None):
        if self.wait_until(self.find_interac):
            if direction is not None:
                self.send_key_up(direction)
                self.sleep(0.40)
            ret = self.wait_until(
                self.has_extract_panel,
                pre_action=lambda: self.send_key("f", interval=1),
                time_out=2.6,
            )
            if ret:
                self.ensure_in_team()
            return ret
        else:
            raise AbortException("not found exit interaction")

    def walk_until_extract_panel(self, direction=None, time_out=10):
        if direction is not None:
            self.send_key_down(direction)
        self.wait_until(
            self.has_extract_panel,
            pre_action=lambda: self.send_key("f", interval=0.25),
            time_out=time_out,
        )
        if direction is not None:
            self.send_key_up(direction)
