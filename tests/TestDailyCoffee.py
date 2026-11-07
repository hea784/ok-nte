import unittest
from unittest.mock import MagicMock

from src.tasks.DailyTask import DailyTask


class TestDailyCoffeeLocaleGate(unittest.TestCase):
    """BnanZ0 PR #86 反馈: 仅在 zh_CN 下暴露一咖舍自动化给 UI."""

    def _patch_locale(self, name=None, *, raise_exc=False, missing_app=False, missing_locale=False):
        from unittest.mock import MagicMock

        if missing_app:
            return self._replace_app(None)

        app = MagicMock()
        if missing_locale:
            del app.locale
        else:
            if raise_exc:
                app.locale.name.side_effect = RuntimeError("locale unavailable")
            else:
                app.locale.name.return_value = name
        return self._replace_app(app)

    def _replace_app(self, app):
        from ok import og

        original_app = getattr(og, "app", None)
        og.app = app
        return original_app

    def _restore_app(self, original_app):
        from ok import og

        og.app = original_app

    def _instantiate(self):
        # 真实 __init__ 路径覆盖 locale 检测 + AnomalyTask.setup_config 等.
        # 提供最小 executor / app mock 以满足 BaseTask.__init__ 签名.
        executor = MagicMock()
        executor.onetime_tasks = []
        executor.trigger_tasks = []
        ctor_app = MagicMock()
        return DailyTask(executor=executor, app=ctor_app)

    def test_missing_locale_attribute_hides_toggle(self):
        # ``og.app`` 存在但没有 ``locale`` 属性 (例如某些 headless 环境).
        # 守卫要求 hasattr(app, "locale") 才会调用 ``locale.name()``.
        original = self._patch_locale(missing_locale=True)
        try:
            task = self._instantiate()
            self.assertNotIn(DailyTask.COFFEE_MODE_AUTO, task.default_config)
            self.assertNotIn(
                DailyTask.COFFEE_MODE_AUTO,
                task.config_type[DailyTask.CONF_COFFEE_TASK]["options"],
            )
        finally:
            self._restore_app(original)

    def test_locale_call_raising_does_not_raise_and_hides_toggle(self):
        original = self._patch_locale(raise_exc=True)
        try:
            task = self._instantiate()
            self.assertNotIn(DailyTask.COFFEE_MODE_AUTO, task.default_config)
            self.assertNotIn(
                DailyTask.COFFEE_MODE_AUTO,
                task.config_type[DailyTask.CONF_COFFEE_TASK]["options"],
            )
        finally:
            self._restore_app(original)

if __name__ == "__main__":
    unittest.main()
