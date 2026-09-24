from src.scene.PanelPosition import PanelPosition
from src.scene.ScreenPosition import ScreenPosition


class PositionMap:
    def __init__(self, parent):
        self.screen = ScreenPosition(parent)
        self.panels = PanelPosition(parent)
