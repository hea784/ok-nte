from src.scene.ScreenPosition import ScreenPosition
from src.scene.ScreenRatio import ScreenRatio


class F5CoffeePosition:
    entry = ScreenRatio(0.335, 0.675)

    def __init__(self, parent):
        self._parent = parent


class F5HousePosition:
    entry = ScreenRatio(0.272, 0.392)

    def __init__(self, parent):
        self._parent = parent


class F5Position:
    def __init__(self, parent):
        self.coffee = F5CoffeePosition(parent)
        self.house = F5HousePosition(parent)


class PositionMap:
    def __init__(self, parent):
        self.screen = ScreenPosition(parent)
        self.f5 = F5Position(parent)
