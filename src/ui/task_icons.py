from typing import Any


class Icon:
    CALENDAR: Any = "calendar"
    GAME: Any = "game"

    @classmethod
    def configure(cls, ui_mode: str | None) -> None:
        match ui_mode:
            case "qt":
                from qfluentwidgets import FluentIcon

                cls.CALENDAR = FluentIcon.CALENDAR
                cls.GAME = FluentIcon.GAME
            case "web":
                cls.CALENDAR = "calendar"
                cls.GAME = "game"
            case _:
                return None
