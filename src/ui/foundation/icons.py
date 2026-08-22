"""Project-provided Fluent icon definitions."""

from enum import Enum

from ok import get_path_relative_to_exe
from qfluentwidgets import FluentIconBase, Theme, getIconColor


class FluentSystemIcon(FluentIconBase, Enum):
    MUSIC_NOTE = "MusicNote1"
    NEXT = "Next"
    PREVIOUS = "Previous"
    HEART_FILL = "HeartFill"
    CHEVRON_DOWN_UP = "Chevron_down_up"
    CHEVRON_UP_DOWN = "Chevron_up_down"

    def path(self, theme=Theme.AUTO):
        path = get_path_relative_to_exe(
            "assets", "fluenticons", f"{self.value}_{getIconColor(theme)}.svg"
        )
        return path or ""
