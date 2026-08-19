from src.char.Support import Support
from src.combat.planner import Planner


class Sakiri(Support):
    cn_name = "早雾"
    element = Support.ElementType.RED

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def combat_plan(self, context):
        return self.plan(
            self.click_ultimate_action(add_tags=Planner.ActionTag.TEAM_BUFF),
            self.click_skill_action(add_tags=Planner.ActionTag.TEAM_BUFF, down_time=0.25),
        )
