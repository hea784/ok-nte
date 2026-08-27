"""Application service for exporting and transactionally installing team packages."""

from dataclasses import dataclass
from pathlib import Path

from src.char.core.CharRegistry import char_registry
from src.char.custom.CustomCharManager import CustomCharManager
from src.char.workshop.archive import (
    ArchiveContents,
    load_archive,
    remap_external_slot,
    write_archive,
)
from src.char.workshop.models import PackageSlot, TeamPackage


class WorkshopInstallError(RuntimeError):
    """Raised when a package cannot be safely installed into local character data."""


@dataclass(frozen=True)
class ImportedTeamPackage:
    preset_id: str
    preset_name: str
    directory: str
    package: TeamPackage


class WorkshopPackageService:
    def __init__(
        self,
        manager: CustomCharManager | None = None,
        registry=char_registry,
    ):
        self.manager = manager or CustomCharManager()
        self.registry = registry

    def export_preset(self, preset_id: str, package: TeamPackage, path: Path) -> None:
        preset = next(
            (item for item in self.manager.get_team_presets() if item["id"] == preset_id), None
        )
        if preset is None:
            raise WorkshopInstallError("team preset was not found")
        slots: list[PackageSlot] = []
        sources: dict[str, str] = {}
        used_names: set[str] = set()
        for index, raw_slot in enumerate(preset["slots"]):
            impl_id = str(raw_slot.get("impl_id", "")).strip()
            if not impl_id:
                continue
            entry = self.registry.get(impl_id)
            if entry is None:
                raise WorkshopInstallError(f"unknown implementation in slot {index + 1}: {impl_id}")
            display = {"zh_CN": entry.cn_name, "en_US": entry.en_name}
            if entry.source == "builtin":
                slots.append(PackageSlot(index, "builtin", display, impl_id=impl_id))
                continue
            if entry.source != "external":
                raise WorkshopInstallError(
                    f"unsupported implementation in slot {index + 1}: {impl_id}"
                )
            source = self.manager.get_external_impl_source(impl_id)
            if not source:
                raise WorkshopInstallError(f"could not read external source in slot {index + 1}")
            base_name = Path(impl_id.removeprefix("external:")).name
            file_name = f"{base_name}.py"
            if file_name in used_names:
                file_name = f"slot_{index + 1}_{file_name}"
            used_names.add(file_name)
            slots.append(
                PackageSlot(
                    index,
                    "external",
                    display,
                    file_name=file_name,
                    class_name=entry.char_cls.__name__,
                )
            )
            sources[file_name] = source
        if not slots:
            raise WorkshopInstallError("team preset has no exportable implementations")
        exported_package = TeamPackage(
            package.name,
            package.description,
            package.author,
            package.version,
            tuple(slots),
        )
        write_archive(path, ArchiveContents(exported_package, sources))

    def load_archive(self, source: Path | bytes) -> ArchiveContents:
        return load_archive(source)

    def install_contents(
        self,
        contents: ArchiveContents,
        preset_name: str,
        directory: str,
    ) -> ImportedTeamPackage:
        try:
            directory = self.manager.validate_external_directory(directory)
        except ValueError as error:
            raise WorkshopInstallError(str(error)) from error
        preset_name = str(preset_name or "").strip()
        if not preset_name:
            raise WorkshopInstallError("team preset name is required")
        for slot in contents.package.slots:
            if slot.kind == "builtin" and not self.manager.is_builtin_impl(slot.impl_id):
                raise WorkshopInstallError(f"unknown builtin implementation: {slot.impl_id}")

        created_preset_id = ""
        installed_sources = False
        try:
            if contents.sources:
                installed, error = self.manager.install_external_sources(
                    directory, contents.sources
                )
                if not installed:
                    raise WorkshopInstallError(error)
                installed_sources = True

            mapped_slots = [{"char_id": "", "impl_id": ""} for _ in range(4)]
            for slot in contents.package.slots:
                impl_id = (
                    slot.impl_id if slot.kind == "builtin" else remap_external_slot(slot, directory)
                )
                if slot.kind == "external":
                    entry = self.registry.get(impl_id)
                    if entry is None or entry.source != "external":
                        raise WorkshopInstallError(
                            f"external implementation could not be loaded: {slot.file_name}"
                        )
                    if entry.char_cls.__name__ != slot.class_name:
                        raise WorkshopInstallError(
                            f"external implementation class does not match: {slot.file_name}"
                        )
                mapped_slots[slot.index] = {"char_id": "", "impl_id": impl_id}

            preset = self.manager.create_team_preset(preset_name)
            created_preset_id = preset["id"]
            if not self.manager.update_team_preset(created_preset_id, slots=mapped_slots):
                raise WorkshopInstallError("could not save imported team preset")
            saved_preset = next(
                item for item in self.manager.get_team_presets() if item["id"] == created_preset_id
            )
            return ImportedTeamPackage(
                created_preset_id,
                saved_preset["name"],
                directory,
                contents.package,
            )
        except Exception:
            if created_preset_id:
                self.manager.delete_team_preset(created_preset_id)
            if installed_sources:
                self.manager.remove_external_sources(directory)
            else:
                self.registry.rescan_external()
            raise

    def import_archive(
        self,
        source: Path | bytes,
        preset_name: str,
        directory: str,
    ) -> ImportedTeamPackage:
        return self.install_contents(self.load_archive(source), preset_name, directory)
