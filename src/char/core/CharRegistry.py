from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from threading import RLock

from ok import Logger

from src.char.BaseChar import BaseChar, Element

logger = Logger.get_logger(__name__)


@dataclass(frozen=True)
class CharImplementation:
    impl_id: str
    source: str
    char_cls: type[BaseChar]
    en_name: str
    cn_name: str
    element: Element

    def display_name(self, locale_name: str = "") -> str:
        return self.cn_name if locale_name == "zh_CN" else self.en_name


class CharRegistry:
    """Discover built-in character implementations without a hand-maintained mapping."""

    def __init__(self):
        self._lock = RLock()
        self._entries: dict[str, CharImplementation] = {}
        self._builtin_scanned = False

    @staticmethod
    def _builtin_dir() -> Path:
        return Path(__file__).resolve().parent.parent

    def get(self, impl_id: str) -> CharImplementation | None:
        self.ensure_builtin_scanned()
        with self._lock:
            return self._entries.get(str(impl_id or ""))

    def get_all(self) -> list[CharImplementation]:
        self.ensure_builtin_scanned()
        with self._lock:
            return sorted(self._entries.values(), key=lambda entry: entry.impl_id)

    def ensure_builtin_scanned(self) -> None:
        if self._builtin_scanned:
            return
        with self._lock:
            if self._builtin_scanned:
                return
            for path in sorted(self._builtin_dir().glob("*.py")):
                self._register_builtin_module(path)
            self._builtin_scanned = True

    def _register_builtin_module(self, path: Path) -> None:
        if path.stem in {"BaseChar", "Support", "__init__"}:
            return
        try:
            module = import_module(f"src.char.{path.stem}")
        except Exception as error:
            logger.warning(f"Failed to import built-in character module {path.name}: {error}")
            return
        candidates = [
            value
            for value in vars(module).values()
            if isinstance(value, type)
            and issubclass(value, BaseChar)
            and value is not BaseChar
            and value.__module__ == module.__name__
            and (value.__dict__.get("en_name") or value.__dict__.get("cn_name"))
        ]
        if len(candidates) != 1:
            return
        char_cls = candidates[0]
        impl_id = f"builtin:{path.stem.lower()}"
        self._entries[impl_id] = CharImplementation(
            impl_id=impl_id,
            source="builtin",
            char_cls=char_cls,
            en_name=char_cls.en_name,
            cn_name=char_cls.cn_name,
            element=char_cls.element,
        )


char_registry = CharRegistry()
