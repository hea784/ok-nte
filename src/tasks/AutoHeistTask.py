import re
import time
from threading import Event

from ok import TaskDisabledException
from qfluentwidgets import FluentIcon

from src.combat.BaseCombatTask import BaseCombatTask
from src.heist_path.HeistPathA import HeistPathA
from src.tasks.NTEOneTimeTask import NTEOneTimeTask
from src.utils import game_filters as gf


class AutoHeistTask(NTEOneTimeTask, BaseCombatTask):
    CONF_LOOP_COUNT = "循环次数"
    CONF_PATH = "路径"
    CONF_NANALLY = "娜娜莉位置"
    CONF_MINT = "薄荷位置"
    CONF_DOGBRO = "狗哥位置"
    CONF_SAKIRI = "早雾位置"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动粉爪大劫案"
        self.icon = FluentIcon.SHOPPING_CART
        self.paths = {
            "路径1": HeistPathA,
        }
        paths_name = list(self.paths.keys())
        self.default_config.update(
            {
                self.CONF_LOOP_COUNT: 0,
                self.CONF_PATH: paths_name[0],
                self.CONF_NANALLY: 1,
                self.CONF_MINT: 2,
                self.CONF_DOGBRO: 3,
                self.CONF_SAKIRI: 4,
            }
        )
        self.config_description.update(
            {
                self.CONF_LOOP_COUNT: "循环次数, 设置为0则一直运行",
                self.CONF_NANALLY: "娜娜莉在几号位 (没有的话或许可以换成其他攻击不会转视角的角色)",
                self.CONF_MINT: "薄荷在几号位",
                self.CONF_DOGBRO: "狗哥在几号位",
                self.CONF_SAKIRI: "早雾在几号位",
            }
        )

        self.config_type.update(
            {
                self.CONF_PATH: {
                    "type": "drop_down",
                    "options": paths_name,
                },
            }
        )
        self._scroll_switch = False
        self._scroll_count = 0
        self.quick_pick = Event()

        self.label = 0
        self.error = 0

    def run(self):
        super().run()
        try:
            return self.do_run()
        except TaskDisabledException:
            pass
        except Exception as e:
            self.log_error("自动银行差事出错", e)
            raise

    def do_run(self):
        self.log_info("spam_key_loop start")
        self.submit_periodic_task(0.01, self._spam_key_loop)
        self.label = ""
        self.error = 0

        count = 0
        earnfcash = 0
        earnpcoin = 0

        total = int(self.config.get(self.CONF_LOOP_COUNT, 1))
        endless = total == 0
        while endless or count < total:
            count += 1
            self.label = f"第 {count} 轮"
            round_text = "∞" if endless else f"{total}"

            self.info_set("轮次", f"{count} / {round_text}")
            self.info_set("失败次数", self.error)
            self.info_add("总方斯获取数", earnfcash)
            self.info_add("总粉爪币获取数", earnpcoin)

            if self.wait_until(self.find_interac, time_out=20, raise_if_not_found=True):
                self.enter_heist()
                if not self.wait_until(self.in_heist, time_out=60):
                    self.heist_error()
                    continue
                self.sleep(1.00)

                if self.run_path() is False:
                    self.heist_error()
                    continue

                earnfcash, earnpcoin = self.exit_heist()

            self.next_frame()

    def custom_log(self, message):
        self.log_info(f"{self.label}: " + message)

    def get_earn(self):
        number_re = re.compile(r"(\d+)")
        earnfcash = 0
        earnpcoin = 0

        cash = self.ocr(
            0.359, 0.595, 0.500, 0.642, frame_processor=gf.isolate_text_to_black, name="cash"
        )
        coin = self.ocr(
            0.654, 0.595, 0.789, 0.641, frame_processor=gf.isolate_text_to_black, name="coin"
        )
        if cash:
            match_1 = number_re.search(cash[0].name.replace(",", ""))
            if match_1:
                earnfcash = int(match_1.group(1))

        if coin:
            match_2 = number_re.search(coin[0].name.replace(",", ""))
            if match_2:
                earnpcoin = int(match_2.group(1))

        return earnfcash, earnpcoin

    def heist_error(self):
        self.custom_log("出现异常，将退出粉爪副本")
        self.error += 1
        self.wait_until(
            lambda: self.ocr(0.46, 0.32, 0.54, 0.37, match=re.compile("确认退出")),
            pre_action=lambda: self.send_key("esc", interval=2),
        )
        btn = self.wait_ocr(0.52, 0.63, 0.68, 0.68, match=re.compile("确认"))
        self.wait_until(
            lambda: not self.ocr(0.46, 0.32, 0.54, 0.37, match=re.compile("确认退出")),
            pre_action=lambda: self.operate_click(btn, interval=1),
        )
        self.wait_in_team(time_out=60)
        self.custom_log("已退出粉爪副本")

    # 进入粉爪副本
    def enter_heist(self):
        def in_panel():
            return self.ocr(0.625, 0.483, 0.685, 0.525, match=re.compile("挑战时间"))

        def action():
            self.send_key("f", action_name="enter_heist_f", interval=1)
            if not self.is_in_team():
                self.sleep(0.1)
                self.send_key("space", action_name="enter_heist_space", interval=1)

        self.wait_until(
            in_panel,
            pre_action=action,
            time_out=20,
        )
        self.sleep(1)
        self.wait_until(
            lambda: not in_panel(),
            pre_action=lambda: self.operate_click(0.7734, 0.8824, interval=1),
            time_out=20,
        )
        self.sleep(1)

    # 离开粉爪副本
    def exit_heist(self):
        def in_exit_panel():
            return self.ocr(0.2602, 0.2639, 0.3520, 0.3257, match=re.compile("安全撤离"))

        def in_sum_panel():
            return self.ocr(0.4496, 0.8354, 0.5547, 0.8868, match=re.compile("退出"))

        self.wait_until(
            in_exit_panel,
            pre_action=lambda: self.send_key("f", interval=1),
        )
        self.sleep(1)
        earnfcash, earnpcoin = self.get_earn()
        self.wait_until(
            lambda: not in_exit_panel(),
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
        self.wait_in_team(time_out=60)
        self.custom_log("已离开粉爪副本")
        return earnfcash, earnpcoin

    def send_key_down(self, key, after_sleep=0):
        if key == "f":
            if not self.quick_pick.is_set():
                self.quick_pick.ready_at = time.time() + 0.3
            self.quick_pick.set()
            self._scroll_switch = False
            return
        return super().send_key_down(key, after_sleep)

    def send_key_up(self, key, after_sleep=0):
        if key == "f":
            self.quick_pick.clear()
            if hasattr(self.quick_pick, "ready_at"):
                del self.quick_pick.ready_at
            return
        return super().send_key_up(key, after_sleep)

    def _spam_key_loop(self):
        if self.quick_pick.is_set() and time.time() >= getattr(self.quick_pick, "ready_at", 0):
            self.send_key("f", interval=0.25)
            self._alternate_scroll(interval=0.25)
        if not self.enabled or not self.running:
            self.log_info("spam_key_loop stop")
            return False

    def _alternate_scroll(self, interval=0):
        if time.time() - self._scroll_time >= interval:
            time.sleep(0.01)
            if self._scroll_switch:
                self.scroll(0, 0, 1)
            else:
                self.scroll(0, 0, -1)
            self._scroll_time = time.time()
            self._scroll_count += 1
            if self._scroll_count >= 3:
                self._scroll_count = 0
                self._scroll_switch = not self._scroll_switch

    def run_path(self):
        path_name = self.config.get(self.CONF_PATH)
        path_cls = self.paths.get(path_name, next(iter(self.paths.values())))
        path = path_cls(self)
        return path.run_path()

    def check_current_floor(self, floor=1):
        """检查是否在指定楼层"""
        floor_str = "LG" + str(floor)
        ret = self.wait_ocr(0.04, 0.235, 0.11, 0.275, match=re.compile("LG.*"), time_out=10)
        if ret:
            return floor_str in ret[0].name
        return False

    def in_heist(self):
        ret = self.ocr(0.023, 0.340, 0.084, 0.379, match=re.compile("本局收益"))
        return bool(ret)
