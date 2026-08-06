from ok import TaskDisabledException
from qfluentwidgets import FluentIcon

from src.combat.BaseCombatTask import BaseCombatTask
from src.Labels import Labels
from src.tasks.NTEOneTimeTask import NTEOneTimeTask


class FurnitureTask(NTEOneTimeTask, BaseCombatTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "异象家具"
        self.icon = FluentIcon.SHOPPING_CART
        self.group_name = "日常/周常"
        self.visible = False

    def run(self):
        super().run()
        try:
            self.do_run()
        except TaskDisabledException:
            raise
        except Exception as e:
            self.log_error("FurnitureTask error", e)
            raise

    def do_run(self):
        return self.claim_anomaly_furniture()

    def claim_anomaly_furniture(self):
        """领取异象家具奖励"""

        self.log_info("正在领取异象家具奖励")

        furniture_list = [
            Labels.anomaly_fluff,
            Labels.anomaly_hamster_ball,
            Labels.anomaly_wooden_crate,
        ]

        furniture_results = {}
        for furniture in furniture_list:
            try:
                claimed = self.claim_furniture(furniture)
            except TaskDisabledException:
                raise
            except Exception as e:
                self.log_error(f"领取异象家具失败: {furniture}", e)
                claimed = False

            furniture_results[furniture] = claimed
            result = "成功" if claimed else "失败"
            self.log_info(f"异象家具 {furniture} 领取{result}")

        all_claimed = all(furniture_results.values())
        if all_claimed:
            self.log_info("异象家具奖励全部领取成功")
        else:
            self.log_error("异象家具奖励未能全部领取成功")
        return all_claimed

    def open_house_panel(self):
        def action():
            self.openF5panel()
            self.operate_click(0.255, 0.468)
            self.sleep(0.5)
            return self.wait_panel(Labels.f5_house_panel)

        if self.find_one(Labels.f5_house_panel):
            return True
        result = self.retry_on_action(action, self.ensure_main)
        if not result:
            self.log_error("无法找到房产面板")
            return False
        self.sleep(1)
        return True

    def check_house_lock(self, ratio_y):
        box = self.box_of_screen(0.050, ratio_y - 0.1, width=0.054, height=0.079, hcenter=True)
        return self.find_one(Labels.f5_house_lock, box=box)

    def teleport_to_furniture(self, furniture):
        house_box = self.box_of_screen(0.507, 0.476, 0.956, 0.795, hcenter=True)

        shown = 4
        ratio_x = 0.079
        ratio_y = 0.308
        gap = 0.183
        scroll_per_item = 6

        scroll = True
        scroll_times = 0
        i = 0
        is_initial = True
        if not self.open_house_panel():
            return False

        # 寻找目标家具
        while scroll or i < shown:
            self.next_frame()
            if scroll:
                target_y = ratio_y
            else:
                target_y = ratio_y + gap * i
                i += 1

            # 检查房子是否解锁
            if self.check_house_lock(target_y):
                self.sleep(0.25)
            else:
                if not is_initial:
                    box = self.get_box_by_name(Labels.box_house_preview_snapshot)
                    snapshot = box.crop_frame(self.frame)
                    for _ in range(10):
                        self.operate_click(ratio_x, target_y)
                        self.sleep(0.25)
                        if not self.find_one(template=snapshot, box=box):
                            break
                        self.sleep(0.25)
                is_initial = False
                if self.find_sift_feature(furniture, box=house_box):
                    break

            # 滚动并检查是否成功滚动
            if scroll:
                scroll_times += 1
                box = self.get_box_by_name(Labels.box_house_list_snapshot)
                snapshot = box.crop_frame(self.frame)
                self.operate(
                    lambda: (
                        self.scroll_relative(ratio_x, ratio_y, -scroll_per_item),
                        self.sleep(0.25),
                    ),
                    block=True,
                )
                y_offset = self.height * 0.1
                search_box = box.copy(y_offset=-y_offset, height_offset=y_offset)
                scroll = not self.find_one(
                    "snapshot", template=snapshot, box=search_box, threshold=0.9
                )
        else:
            self.log_info(f"not found furniture {furniture}")
            self.operate(
                lambda: (
                    self.scroll_relative(ratio_x, ratio_y, scroll_per_item * (scroll_times + 2)),
                    self.sleep(0.25),
                ),
                block=True,
            )
            return False

        # 传送至目标房子
        self.wait_until(
            lambda: not self.find_one(Labels.f5_house_panel),
            pre_action=lambda: self.operate_click(0.891, 0.951, after_sleep=1),
        )
        self.click_traval_button()
        return self.wait_in_team(time_out=120, settle_time=1)

    def claim_furniture(self, furniture):
        if not self.teleport_to_furniture(furniture):
            return False

        # 打开异象家具
        def action_1():
            try:
                self.send_key_down("lalt")
                self.sleep(0.25)
                self.operate_click(0.465, 0.056)
            finally:
                self.send_key_up("lalt")
            self.sleep(2)
            if not self.is_in_team():
                return True

        self.retry_on_action(action_1, attempt=10, raise_if_failed=True)
        box_left = self.box_of_screen(0.024, 0.181, 0.278, 0.775, hcenter=True)
        self.wait_until(
            lambda: self.find_sift_feature(furniture, box=box_left), raise_if_not_found=True
        )
        self.sleep(0.5)
        box_right = self.box_of_screen(0.738, 0.236, 0.805, 0.959, hcenter=True)

        # 点击异象家具
        def action_2():
            box = self.find_sift_feature(furniture, box=box_left)
            if box:
                self.operate_click(box)
                self.sleep(0.5)
                self.operate_click(0.924, 0.174)
                self.sleep(0.5)
                if self.find_sift_feature(furniture, box=box_right):
                    return True
            self.sleep(0.5)

        self.retry_on_action(action_2, attempt=10, raise_if_failed=True)

        # 二次确认异象家具
        self.wait_until(
            lambda: self.find_sift_feature(furniture, box=box_right), raise_if_not_found=True
        )

        # 领取目标家具
        self.sleep(0.5)
        self.operate(
            lambda: (
                self.click(0.938, 0.283, move=True),
                self.sleep(0.1),
                self.click(0.938, 0.303, move=True),
            ),
            block=True,
        )
        self.sleep(0.5)
        self.after_claim_action(furniture)
        self.ensure_main()
        return True

    def after_claim_action(self, furniture):
        match furniture:
            case "mammon":
                self.perform_mammon()
            case _:
                pass

    def perform_mammon(self):
        pass