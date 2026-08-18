from src.char.BaseChar import BaseChar
from src.combat.planner import Planner, RoleProfile


class Support(BaseChar):
    def describe_role(self):
        return RoleProfile(
            role=Planner.Role.SUPPORT,
            field_preference=Planner.FieldPreference.SUPPORT,
            max_field_time=1,
            combat_start_priority=1
        )

    def click_ultimate_action(
        self,
        name: str | None = None,
        tags: set[Planner.ActionTag] | None = None,
        add_tags: set[Planner.ActionTag] | Planner.ActionTag | None = None,
        reason: str = "ultimate action available",
        can_execute=None,
    ):
        tags = tags or {Planner.ActionTag.ULTIMATE_ACTION, Planner.ActionTag.SUPPORT}
        return super().click_ultimate_action(
            name=name,
            tags=tags,
            add_tags=add_tags,
            reason=reason,
            can_execute=can_execute,
        )

    def click_skill_action(
        self,
        name: str | None = None,
        tags: set[Planner.ActionTag] | None = None,
        add_tags: set[Planner.ActionTag] | Planner.ActionTag | None = None,
        reason: str = "skill action available",
        down_time: float = 0.01,
        can_execute=None,
    ):
        tags = tags or {Planner.ActionTag.SKILL_ACTION, Planner.ActionTag.SUPPORT}
        return super().click_skill_action(
            name=name,
            tags=tags,
            add_tags=add_tags,
            reason=reason,
            down_time=down_time,
            can_execute=can_execute,
        )
