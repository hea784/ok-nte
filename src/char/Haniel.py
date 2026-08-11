from src.char.BaseChar import BaseChar
from src.combat.planner import (
    CombatContext,
    FieldPreference,
    Role,
    RoleProfile,
)

SKILL_SHORT_TIMEOUT = 2.0


class Haniel(BaseChar):
    """Haniel - BLUE support.

    SUB_DPS, SETUP_ONLY: Q to deploy the enhanced domain, then E to deploy the
    companion, then leave the field. Self-contained and independent of any specific
    team composition; higher-level coordination is handled outside this file.
    """

    cn_name = "哈妮娅"
    element = BaseChar.Element.BLUE

    def describe_role(self):
        return RoleProfile(
            role=Role.SUB_DPS,
            field_preference=FieldPreference.SETUP_ONLY,
            max_field_time=0,
        )

    def combat_plan(self, context: CombatContext):
        ultimate = self.click_ultimate_action()
        skill = self.click_skill_action()

        def entry():
            ultimate_result = yield ultimate
            if ultimate_result:
                self.sleep(0.3)
            skill_result = yield skill
            if skill_result:
                self.sleep(0.3)

        return self.plan(ultimate, skill, entry=entry)
