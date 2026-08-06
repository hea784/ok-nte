from dataclasses import dataclass
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from sys import modules
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
    """Discover built-in and external character implementations without a manual mapping."""

    def __init__(self, external_dir: Path | None = None):
        self._lock = RLock()
        self._entries: dict[str, CharImplementation] = {}
        self._builtin_scanned = False
        self._external_scanned = False
        self._external_dir = external_dir

    @staticmethod
    def _builtin_dir() -> Path:
        return Path(__file__).resolve().parent.parent

    def get(self, impl_id: str) -> CharImplementation | None:
        self.ensure_scanned()
        with self._lock:
            return self._entries.get(str(impl_id or ""))

    def get_all(self) -> list[CharImplementation]:
        self.ensure_scanned()
        with self._lock:
            return sorted(self._entries.values(), key=lambda entry: entry.impl_id)

    def rescan_external(self) -> None:
        """Rediscover external character modules without reloading built-ins."""
        with self._lock:
            self._entries = {
                impl_id: entry
                for impl_id, entry in self._entries.items()
                if entry.source != "external"
            }
            self._scan_external()

    def ensure_scanned(self) -> None:
        if self._builtin_scanned and self._external_scanned:
            return
        with self._lock:
            if not self._builtin_scanned:
                for path in sorted(self._builtin_dir().glob("*.py")):
                    self._register_builtin_module(path)
                self._builtin_scanned = True
            if not self._external_scanned:
                self._scan_external()

    def _scan_external(self) -> None:
        try:
            external_paths = sorted(self._get_external_dir().glob("*.py"))
        except OSError as error:
            logger.warning(f"Failed to scan external character modules: {error.__class__.__name__}")
            external_paths = []
        for path in external_paths:
            self._register_external_module(path)
        self._external_scanned = True

    def _get_external_dir(self) -> Path:
        if self._external_dir is not None:
            return self._external_dir
        from src.char.custom.CustomCharManager import EXTERNAL_CHARS_DIR

        return Path(EXTERNAL_CHARS_DIR)

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

    def _register_external_module(self, path: Path) -> None:
        if path.stem.startswith("_"):
            return
        module_name = f"ok_nte_external_{path.stem.lower()}"
        try:
            spec = spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise ImportError("no module loader")
            module = module_from_spec(spec)
            modules[module_name] = module
            spec.loader.exec_module(module)
        except Exception as error:
            modules.pop(module_name, None)
            logger.warning(
                "Failed to import external character module "
                f"{path.name}: {error.__class__.__name__}"
            )
            return

        candidates = [
            value
            for value in vars(module).values()
            if isinstance(value, type)
            and issubclass(value, BaseChar)
            and value is not BaseChar
            and value.__module__ == module.__name__
        ]
        if len(candidates) != 1:
            logger.warning(
                f"External character module {path.name} must define exactly one BaseChar subclass"
            )
            return

        char_cls = candidates[0]
        impl_id = f"external:{char_cls.__name__.lower()}"
        if impl_id in self._entries:
            logger.warning(f"Duplicate external character implementation {impl_id} in {path.name}")
            return
        self._entries[impl_id] = CharImplementation(
            impl_id=impl_id,
            source="external",
            char_cls=char_cls,
            en_name=char_cls.en_name,
            cn_name=char_cls.cn_name,
            element=char_cls.element,
        )


char_registry = CharRegistry()
