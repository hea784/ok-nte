import ast
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MigrationContext:
    is_builtin_impl: Callable[[str], bool]
    get_builtin_prefix: Callable[[], str]
    iter_builtin_impl_items: Callable[[], Iterable[tuple[str, str]]]
    generate_combo_id: Callable[[set[str] | None], str]
    get_external_impl_ids_by_class_name: Callable[[str], Iterable[str]] = lambda _class_name: ()


@dataclass
class MigrationResult:
    db: dict
    modified: bool = False
    needs_backup: bool = False
    diagnostics: list[str] = field(default_factory=list)


class CustomCharDbMigrator:
    """Convert historical custom-character schemas without performing file I/O."""

    LEGACY_LAYOUT_SCHEMA_VERSION = 5
    LEGACY_BUILTIN_PREFIX = "builtin:"
    LEGACY_KEY_PATTERN = re.compile(r"\(([^)]+)\)\s*$")
    LEGACY_BUILTIN_IDS = {
        "char_zero": "builtin:zero",
        "char_mint": "builtin:mint",
        "char_jiuyuan": "builtin:jiuyuan",
        "char_sakiri": "builtin:sakiri",
        "char_nanally": "builtin:nanally",
        "char_hotori": "builtin:hotori",
        "char_chiz": "builtin:chiz",
        "char_lacrimosa": "builtin:lacrimosa",
        "char_fadia": "builtin:fadia",
        "char_shinku": "builtin:shinku",
        "char_iroi": "builtin:iroi",
    }

    def __init__(self, context: MigrationContext, target_schema_version: int):
        self._context = context
        self._target_schema_version = target_schema_version

    def migrate(self, db: dict) -> MigrationResult:
        """Advance an older persisted schema through explicit in-memory stages."""
        source_version = self._schema_version(db)
        if source_version >= self._target_schema_version:
            return MigrationResult(db=db)

        if source_version < self.LEGACY_LAYOUT_SCHEMA_VERSION:
            db = self._migrate_legacy_layout_to_v5(db)

        db, diagnostics = self._migrate_combo_syntax_to_current(db)
        self._migrate_impl_ids(db)
        if source_version < 8:
            diagnostics.extend(self._migrate_external_impl_ids(db))
        return MigrationResult(db=db, modified=True, needs_backup=True, diagnostics=diagnostics)

    def _migrate_impl_ids(self, db: dict) -> None:
        def impl_id(value) -> str:
            value = self._as_text(value).strip()
            return self.LEGACY_BUILTIN_IDS.get(value, value)

        characters = db.get("characters", {})
        if isinstance(characters, dict):
            for record in characters.values():
                if isinstance(record, dict) and "combo_id" in record:
                    record["impl_id"] = impl_id(record.pop("combo_id"))

        fixed_team = db.get("fixed_team", {})
        if isinstance(fixed_team, dict) and isinstance(fixed_team.get("slots"), list):
            for slot in fixed_team["slots"]:
                if isinstance(slot, dict) and "combo_id" in slot:
                    slot["impl_id"] = impl_id(slot.pop("combo_id"))

    def _migrate_external_impl_ids(self, db: dict) -> list[str]:
        diagnostics = []

        def migrate(record: dict) -> None:
            impl_id = self._as_text(record.get("impl_id", "")).strip()
            if not impl_id.startswith("external:"):
                return
            class_name = impl_id.removeprefix("external:")
            matching_impl_ids = list(
                self._context.get_external_impl_ids_by_class_name(class_name)
            )
            if len(matching_impl_ids) == 1:
                record["impl_id"] = matching_impl_ids[0]
            else:
                reason = "ambiguous" if matching_impl_ids else "not found"
                diagnostics.append(
                    f"External character implementation '{impl_id}' could not be migrated: {reason}"
                )

        characters = db.get("characters", {})
        if isinstance(characters, dict):
            for record in characters.values():
                if isinstance(record, dict):
                    migrate(record)

        fixed_team = db.get("fixed_team", {})
        if isinstance(fixed_team, dict) and isinstance(fixed_team.get("slots"), list):
            for slot in fixed_team["slots"]:
                if isinstance(slot, dict):
                    migrate(slot)
        return diagnostics

    @staticmethod
    def _as_text(value) -> str:
        return "" if value is None else str(value)

    @classmethod
    def _is_blank_text(cls, value) -> bool:
        return cls._as_text(value).strip() == ""

    @staticmethod
    def _default_fixed_team() -> dict:
        return {"enabled": False, "slots": [{"char_id": "", "combo_id": ""} for _ in range(4)]}

    @classmethod
    def _unique_name(cls, name: str, used_names: set[str]) -> str:
        name = name.strip()
        if cls._is_blank_text(name):
            name = "unnamed"
        candidate = name
        suffix = 2
        while candidate in used_names:
            candidate = f"{name}_{suffix}"
            suffix += 1
        used_names.add(candidate)
        return candidate

    def _legacy_builtin_label_to_combo_id(self, value: str) -> str | None:
        if not value:
            return None

        prefixes = [self._context.get_builtin_prefix(), "[内置代码] "]
        prefix = next((prefix for prefix in prefixes if value.startswith(prefix)), "")
        if not prefix:
            return None

        label = value.replace(prefix, "", 1).strip()
        match = self.LEGACY_KEY_PATTERN.search(label)
        if match:
            key = match.group(1).strip()
            if self._context.is_builtin_impl(key):
                return key

        if self._context.is_builtin_impl(label):
            return label

        matched_ids = [
            combo_id
            for combo_name, combo_id in self._context.iter_builtin_impl_items()
            if combo_name == label
        ]
        return matched_ids[0] if len(matched_ids) == 1 else None

    def _legacy_value_to_combo_id(self, value: str, combo_id_remap: dict[str, str]) -> str:
        value = self._as_text(value).strip()
        if not value:
            return ""
        if value in combo_id_remap:
            return combo_id_remap[value]
        if value.startswith(self.LEGACY_BUILTIN_PREFIX):
            key = value[len(self.LEGACY_BUILTIN_PREFIX) :].strip()
            if key in self.LEGACY_BUILTIN_IDS:
                return self.LEGACY_BUILTIN_IDS[key]
            if self._context.is_builtin_impl(key):
                return key
        if self._context.is_builtin_impl(value):
            return value
        legacy_builtin_id = self._legacy_builtin_label_to_combo_id(value)
        return legacy_builtin_id or value

    @staticmethod
    def _schema_version(db: dict) -> int:
        try:
            return int(db.get("schema_version", 0))
        except (TypeError, ValueError):
            return 0

    def _migrate_legacy_layout_to_v5(self, db: dict) -> dict:
        raw_combos = db.get("combos", {})
        raw_characters = db.get("characters", {})
        raw_features = db.get("features", {})
        raw_fixed_team = db.get("fixed_team", self._default_fixed_team())
        raw_combos = raw_combos if isinstance(raw_combos, dict) else {}
        raw_characters = raw_characters if isinstance(raw_characters, dict) else {}
        raw_features = raw_features if isinstance(raw_features, dict) else {}

        normalized_combos = {}
        combo_id_remap = {}
        existing_combo_ids = set()
        for old_combo_key, combo_content in raw_combos.items():
            old_combo_key = self._as_text(old_combo_key)
            if self._is_blank_text(old_combo_key):
                continue
            combo_id = self._context.generate_combo_id(existing_combo_ids)
            existing_combo_ids.add(combo_id)
            combo_id_remap[old_combo_key.strip()] = combo_id
            normalized_combos[combo_id] = {
                "name": old_combo_key.strip(),
                "content": self._as_text(combo_content),
            }

        normalized_characters = {}
        used_names = set()
        legacy_id_index = 1

        def next_legacy_id() -> str:
            nonlocal legacy_id_index
            while True:
                candidate = f"char_{legacy_id_index:04d}"
                legacy_id_index += 1
                if candidate not in normalized_characters:
                    return candidate

        for raw_char_id, raw_char_data in raw_characters.items():
            source_data = raw_char_data if isinstance(raw_char_data, dict) else {}
            raw_char_id = self._as_text(raw_char_id).strip()
            if "name" in source_data:
                char_name = self._as_text(source_data.get("name", "")).strip()
                char_id = raw_char_id if raw_char_id else next_legacy_id()
            else:
                char_name = raw_char_id
                char_id = next_legacy_id()
            char_name = self._unique_name(char_name, used_names)

            combo_value = self._as_text(source_data.get("combo_id", ""))
            if not combo_value:
                combo_value = self._as_text(source_data.get("combo_ref", ""))
            if not combo_value:
                combo_value = self._as_text(source_data.get("combo_name", ""))
            combo_id = self._legacy_value_to_combo_id(combo_value, combo_id_remap)
            if (
                combo_id
                and not self._context.is_builtin_impl(combo_id)
                and combo_id not in normalized_combos
            ):
                combo_id = ""

            feature_ids = source_data.get("feature_ids", [])
            if not isinstance(feature_ids, list):
                feature_ids = []

            while char_id in normalized_characters:
                char_id = next_legacy_id()
            normalized_characters[char_id] = {
                "name": char_name,
                "combo_id": combo_id,
                "feature_ids": feature_ids,
            }

        normalized_fixed_team = self._default_fixed_team()
        if isinstance(raw_fixed_team, dict):
            normalized_fixed_team["enabled"] = bool(raw_fixed_team.get("enabled", False))
            raw_slots = raw_fixed_team.get("slots", [])
            if isinstance(raw_slots, list):
                for index in range(min(4, len(raw_slots))):
                    slot = raw_slots[index] if isinstance(raw_slots[index], dict) else {}
                    char_name = self._as_text(slot.get("char_name", "")).strip()
                    combo_value = self._as_text(slot.get("combo_id", ""))
                    if not combo_value:
                        combo_value = self._as_text(slot.get("combo_ref", ""))
                    combo_id = self._legacy_value_to_combo_id(combo_value, combo_id_remap)
                    char_id = next(
                        (
                            char_id
                            for char_id, char_data in normalized_characters.items()
                            if char_data["name"] == char_name
                        ),
                        "",
                    )
                    if self._is_blank_text(char_id):
                        combo_id = ""
                    normalized_fixed_team["slots"][index] = {
                        "char_id": char_id,
                        "combo_id": combo_id,
                    }

        return {
            "schema_version": self.LEGACY_LAYOUT_SCHEMA_VERSION,
            "combos": normalized_combos,
            "characters": normalized_characters,
            "features": raw_features,
            "fixed_team": normalized_fixed_team,
        }

    @staticmethod
    def _contains_legacy_if(node) -> bool:
        return any(
            isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Name)
            and candidate.func.id == "if_"
            for candidate in ast.walk(node)
        )

    @staticmethod
    def _legacy_combo_nodes(tree: ast.Module) -> tuple[list[ast.expr] | None, str | None]:
        nodes = []
        for statement in tree.body:
            if not isinstance(statement, ast.Expr):
                return None, "only command expressions can be migrated"
            expression = statement.value
            nodes.extend(expression.elts if isinstance(expression, ast.Tuple) else [expression])
        return nodes, None

    def _migrate_legacy_combo_content(self, content: str) -> tuple[str, str | None]:
        try:
            tree = ast.parse(content)
        except SyntaxError as error:
            return content, f"cannot parse legacy combo: {error.msg}"

        if not self._contains_legacy_if(tree):
            return content, None

        nodes, error = self._legacy_combo_nodes(tree)
        if error:
            return content, error

        lines = []
        command_buffer = []

        def flush_commands():
            if command_buffer:
                lines.append(", ".join(command_buffer))
                command_buffer.clear()

        for node in nodes or []:
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "if_"
            ):
                if self._contains_legacy_if(node):
                    return content, "nested if_ cannot be migrated"
                command_buffer.append(ast.unparse(node))
                continue

            if node.keywords or len(node.args) < 2:
                return content, "if_ requires a condition and at least one positional action"
            if any(self._contains_legacy_if(argument) for argument in node.args):
                return content, "nested if_ cannot be migrated"

            flush_commands()
            condition = ast.unparse(node.args[0])
            actions = ", ".join(ast.unparse(action) for action in node.args[1:])
            lines.append(f"if {condition}: {actions}")

        flush_commands()
        return "\n".join(lines), None

    def _migrate_combo_syntax_to_current(self, db: dict) -> tuple[dict, list[str]]:
        diagnostics = []
        combos = db.get("combos", {})
        if not isinstance(combos, dict):
            combos = {}
            db["combos"] = combos

        for combo_id, combo_data in combos.items():
            if not isinstance(combo_data, dict):
                continue
            content = self._as_text(combo_data.get("content", ""))
            migrated_content, error = self._migrate_legacy_combo_content(content)
            if error:
                combo_name = self._as_text(combo_data.get("name", combo_id))
                diagnostics.append(f"Combo '{combo_name}' ({combo_id}) was not converted: {error}")
                continue
            if migrated_content != content:
                combo_data["content"] = migrated_content

        db["schema_version"] = self._target_schema_version
        return db, diagnostics
