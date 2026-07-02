from ok import TaskDisabledException
from qfluentwidgets import FluentIcon

from src.combat.BaseCombatTask import BaseCombatTask
from src.Labels import Labels
from src.tasks.BaseNTETask import Box
from src.tasks.NTEOneTimeTask import NTEOneTimeTask


class DSDFarmTask(NTEOneTimeTask, BaseCombatTask):
    CONF_LOCATION = "位置"
    CONF_ROUNDS = "循环次数"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "九百九十九夜"
        self.description = "挂机刷经验"
        self.icon = FluentIcon.FLAG
        self.locations = ["巧克力火山-底层最左边的篝火"]
        self.default_config.update(
            {
                self.CONF_LOCATION: self.locations[0],
                self.CONF_ROUNDS: 0,
            }
        )

        self.config_description.update(
            {
                self.CONF_ROUNDS: "循环次数, 设置为0则一直运行",
            }
        )

        self.config_type.update(
            {
                self.CONF_LOCATION: {
                    "type": "drop_down",
                    "options": self.locations,
                },
            }
        )

    def run(self):
        super().run()
        try:
            self.sleep_check_skip.all = True
            self.do_run()
        except TaskDisabledException:
            pass
        except Exception as e:
            self.log_error("DSDFarmTask Error", e)
        finally:
            self.sleep_check_skip.all = False

    def do_run(self):
        self.map_zoom_max()
        n = 0
        while True:
            n += 1
            rounds = self.config.get(self.CONF_ROUNDS, 0)
            if rounds == 0:
                rounds_text = f"{n} / ∞"
            elif n > rounds:
                return
            else:
                rounds_text = f"{n} / {rounds}"
            self.info_set("轮次", rounds_text)
            self.wait_until(
                self.find_interac,
                time_out=10,
                raise_if_not_found=True,
            )
            self.wait_until(
                lambda: not self.is_in_team(),
                pre_action=lambda: self.send_interac(handle_claim=False),
                time_out=10,
                raise_if_not_found=True,
            )
            self.sleep(2)
            self.operate_click(0.057, 0.218)
            self.sleep(0.5)
            self.ensure_main()
            if self.walk_until_combat(run=True, delay=1):
                with self.skip_sleep_checks() as skip:
                    skip.all = False
                    self.combat_once()
            self.sleep(0.5)
            while True:
                if self.teleport_to_bonfire():
                    break
                self.ensure_main()
                self.sleep(0.5)
            self.next_frame()

    def sleep_check(self):
        super().sleep_check()
        if self.should_check_monthly_card():
            self.handle_monthly_card()

    def map_zoom_max(self):
        self.ensure_main()
        self.open_map()
        self.operate_click(0.050, 0.378)
        self.sleep(1)
        self.ensure_main()

    def open_map(self):
        self.wait_until(
            lambda: self.find_one(Labels.map_zoom_in),
            time_out=10,
            pre_action=lambda: self.send_key("m", interval=2),
            raise_if_not_found=True,
        )
        self.sleep(1)

    def teleport_to_bonfire(self, threshold=0.7, time_out=10):
        self.ensure_main()
        self.open_map()
        to_find = [Labels.bonfire_teleport]
        template_boxes = [self.get_box_by_name(label) for label in to_find]
        max_template_size = max(
            max(template_box.width, template_box.height) for template_box in template_boxes
        )
        step = max(max_template_size, self.width_of_screen(0.02), 1)
        center_x = self.width_of_screen(0.5)
        center_y = self.height_of_screen(0.5)
        max_radius = max(self.width, self.height)

        def find_teleport():
            radius = step
            while radius <= max_radius:
                x = max(0, center_x - radius)
                y = max(0, center_y - radius)
                to_x = min(self.width, center_x + radius)
                to_y = min(self.height, center_y + radius)
                box = Box(x=x, y=y, to_x=to_x, to_y=to_y, name="nearest_map_teleport")
                teleport = self.find_best_match_in_box(box, to_find, threshold=threshold)
                if teleport:
                    return teleport
                radius += step

        teleport = self.wait_until(find_teleport, time_out=time_out, raise_if_not_found=True)
        self.log_info(f"found nearest map teleport {teleport}")
        self.operate_click(teleport, action_name="click_nearest_map_teleport", interval=1)
        self.sleep(0.5)
        return self.click_traval_button(raise_if_not_found=False)