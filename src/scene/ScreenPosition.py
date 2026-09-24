from src.scene.ScreenRatio import ScreenRatio


class ScreenPosition:
    """Common screen positions, expressed as normalized ScreenRatio mappings."""

    center = ScreenRatio(0.25, 0.25, 0.75, 0.75)
    dialog_icon = ScreenRatio(0.845, 0.047, 0.975, 0.074)
    main_viewport = ScreenRatio(0.0984, 0.1042, 0.8961, 0.8944)

    def __init__(self, parent):
        self._parent = parent
