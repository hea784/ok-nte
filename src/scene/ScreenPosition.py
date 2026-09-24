from src.scene.ScreenRatio import ScreenRatio


class ScreenPosition:
    """Common screen positions, expressed as normalized ScreenRatio mappings."""

    center = ScreenRatio(0.25, 0.25, 0.75, 0.75)
    dialog_icon_box = ScreenRatio(0.845, 0.047, 0.975, 0.074)

    def __init__(self, parent):
        self._parent = parent
