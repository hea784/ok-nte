from ok import TaskDisabledException
from qfluentwidgets import FluentIcon

from src.char.core.CharFactory import get_char_implementation_class, iter_char_implementations
from src.combat.BaseCombatTask import BaseCombatTask


class DebugCharTask(BaseCombatTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Test Char"
        self.description = "Test Char"
        self.icon = FluentIcon.SYNC
        self.char = None
        self.is_char_loaded = False
        self.char_list = [entry.impl_id for entry in iter_char_implementations()]
        self.default_config.update({"char": self.char_list[0]})
        self.config_type.update(
            {
                "char": {
                    "type": "drop_down",
                    "options": self.char_list,
                },
            }
        )

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
        while True:
            # self.log_info(self.has_team_skill_records())
            self.sleep(0.1)

    @staticmethod
    def _normalize_impl_id(impl_id):
        impl_id = str(impl_id)
        if impl_id.startswith("char_"):
            return f"builtin:{impl_id.removeprefix('char_')}"
        return impl_id

    def _selected_impl_id(self, warn=False):
        impl_id = self._normalize_impl_id(self.config["char"])
        if get_char_implementation_class(impl_id) is not None:
            return impl_id

        fallback_id = self.char_list[0]
        if warn:
            self.log_warning(
                f"Unknown character implementation '{impl_id}'; using '{fallback_id}' instead"
            )
        return fallback_id

    def init_char(self):
        self.current_char = self._selected_impl_id(warn=True)
        char_class = get_char_implementation_class(self.current_char)
        self.char = char_class(self, 0, char_id=self.current_char, confidence=1)  # type: ignore

    def __getattr__(self, name):
        """
        当调用的属性或方法在当前类中找不到时，会进入这个函数。
        name 是调用的名子（字符串）。
        """
        try:
            if self.char is None or self.current_char != self._selected_impl_id():
                self.is_char_loaded = False
                self.init_char()
            if hasattr(self.char, name):
                if not self.is_char_loaded:
                    self.is_char_loaded = True
                    self.load_chars()
                return getattr(self.char, name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' or its member 'char' has no attribute '{name}'"
            )
        return super().__getattr__(name)
