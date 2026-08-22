"""Reusable card widgets."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from qfluentwidgets import CardWidget, isDarkTheme


class BorderCardWidget(CardWidget):
    def __init__(self, parent=None, border_width: float = 1.0, border_color=None):
        super().__init__(parent)
        self._border_width = max(0.0, border_width)
        self._border_color = None
        self.setBorderColor(border_color)

    def borderWidth(self) -> float:
        return self._border_width

    def setBorderWidth(self, width: float):
        width = max(0.0, width)
        if self._border_width != width:
            self._border_width = width
            self.update()

    def borderColor(self) -> QColor | None:
        return QColor(self._border_color) if self._border_color is not None else None

    def setBorderColor(self, color):
        border_color = None if color is None else QColor(color)
        if border_color is not None and not border_color.isValid():
            raise ValueError(f"Invalid border color: {color!r}")
        if self._border_color != border_color:
            self._border_color = border_color
            self.update()

    def paintEvent(self, event): # type: ignore
        if self._border_width == 1 and self._border_color is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        width, height = self.width(), self.height()
        radius = self.borderRadius
        diameter = 2 * radius
        border_width = min(self._border_width, width, height)
        top_border_color = QColor(0, 0, 0, 20)
        if isDarkTheme():
            if self.isPressed:
                top_border_color = QColor(255, 255, 255, 18)
            elif self.isHover:
                top_border_color = QColor(255, 255, 255, 13)
        else:
            top_border_color = QColor(0, 0, 0, 15)
        bottom_border_color = top_border_color
        if not isDarkTheme() and self.isHover and not self.isPressed:
            bottom_border_color = QColor(0, 0, 0, 27)
        if self._border_color is not None:
            top_border_color = bottom_border_color = self._border_color

        if border_width > 1:
            inset = border_width / 2
            radius = max(0, min(radius, width / 2, height / 2) - inset)
            diameter = 2 * radius
            left, top = inset, inset
            right, bottom = width - inset, height - inset
            path = QPainterPath()
            path.arcMoveTo(left, bottom - diameter, diameter, diameter, 225)
            path.arcTo(left, bottom - diameter, diameter, diameter, 225, -60)
            path.lineTo(left, top + radius)
            path.arcTo(left, top, diameter, diameter, -180, -90)
            path.lineTo(right - radius, top)
            path.arcTo(right - diameter, top, diameter, diameter, 90, -90)
            path.lineTo(right, bottom - radius)
            path.arcTo(right - diameter, bottom - diameter, diameter, diameter, 0, -45)
            pen = QPen(top_border_color, border_width)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            painter.strokePath(path, pen)
            path = QPainterPath()
            path.arcMoveTo(left, bottom - diameter, diameter, diameter, 225)
            path.arcTo(left, bottom - diameter, diameter, diameter, 225, 45)
            path.lineTo(right - radius, bottom)
            path.arcTo(right - diameter, bottom - diameter, diameter, diameter, 270, 45)
            pen = QPen(bottom_border_color, border_width)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            painter.strokePath(path, pen)
        elif border_width > 0:
            path = QPainterPath()
            path.arcMoveTo(1, height - diameter - 1, diameter, diameter, 240)
            path.arcTo(1, height - diameter - 1, diameter, diameter, 225, -60)
            path.lineTo(1, radius)
            path.arcTo(1, 1, diameter, diameter, -180, -90)
            path.lineTo(width - radius, 1)
            path.arcTo(width - diameter - 1, 1, diameter, diameter, 90, -90)
            path.lineTo(width - 1, height - radius)
            path.arcTo(width - diameter - 1, height - diameter - 1, diameter, diameter, 0, -60)
            painter.strokePath(path, top_border_color)
            path = QPainterPath()
            path.arcMoveTo(1, height - diameter - 1, diameter, diameter, 240)
            path.arcTo(1, height - diameter - 1, diameter, diameter, 240, 30)
            path.lineTo(width - radius - 1, height - 1)
            path.arcTo(width - diameter - 1, height - diameter - 1, diameter, diameter, 270, 30)
            painter.strokePath(path, bottom_border_color)

        painter.setPen(Qt.PenStyle.NoPen)
        if border_width > 1:
            inset = border_width / 2
            rect = self.rect().adjusted(inset, inset, -inset, -inset)
            painter.setBrush(self.backgroundColor)
            painter.drawRoundedRect(rect, radius, radius)
        else:
            rect = self.rect().adjusted(1, 1, -1, -1)
            painter.setBrush(self.backgroundColor)
            painter.drawRoundedRect(rect, radius, radius)
