"""Shared Qt overlay host for application interaction events."""

from __future__ import annotations

import win32api
from PySide6.QtCore import QPoint, QRect, QRectF, Qt, QTimer, Slot
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from src.events import (
    OverlayCleared,
    OverlayShown,
    RecordingOverlayContent,
    communicate,
)


class OverlayWindow(QWidget):
    """Click-through overlay that follows the captured game content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlays = {}
        self._capture_visible = False
        self._scaling = 1.0
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(33)
        self._refresh_timer.timeout.connect(self._refresh)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.WindowTransparentForInput
        )

    @Slot(object)
    def show_overlay(self, request: OverlayShown) -> None:
        self._overlays[request.key] = request.content
        self._sync_capture_geometry()
        self._refresh_timer.start()
        self.update()

    @Slot(object)
    def clear_overlay(self, request: OverlayCleared) -> None:
        self._overlays.pop(request.key, None)
        if self._overlays:
            self.update()
            return
        self._refresh_timer.stop()
        self.hide()

    @Slot(bool, int, int, int, int, int, int, float)
    def update_capture_geometry(
        self,
        visible: bool,
        x: int,
        y: int,
        _window_width: int,
        _window_height: int,
        width: int,
        height: int,
        scaling: float,
    ) -> None:
        self._capture_visible = bool(visible)
        self._scaling = max(float(scaling or 1.0), 0.1)
        geometry = QRect(
            round(x / self._scaling),
            round(y / self._scaling),
            max(1, round(width / self._scaling)),
            max(1, round(height / self._scaling)),
        )
        if geometry != self.geometry():
            self.setGeometry(geometry)
        if self._overlays and self._capture_visible:
            self.show()
            self.raise_()
        else:
            self.hide()

    def _refresh(self) -> None:
        if not self._overlays:
            self._refresh_timer.stop()
            return
        self._sync_capture_geometry()
        if self.isVisible():
            self.update()

    def _sync_capture_geometry(self) -> None:
        from ok import og

        hwnd_window = getattr(getattr(og, "device_manager", None), "hwnd_window", None)
        if hwnd_window is None:
            self.hide()
            return
        x, y = hwnd_window.get_capture_origin()
        self.update_capture_geometry(
            bool(getattr(hwnd_window, "visible", False)),
            x,
            y,
            getattr(hwnd_window, "window_width", 0),
            getattr(hwnd_window, "window_height", 0),
            getattr(hwnd_window, "width", 0),
            getattr(hwnd_window, "height", 0),
            getattr(hwnd_window, "scaling", 1.0),
        )

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        mouse_position = self._mouse_position()
        for content in self._overlays.values():
            if isinstance(content, RecordingOverlayContent):
                self._paint_recording_overlay(painter, mouse_position, content)

    def _mouse_position(self) -> QPoint:
        screen_x, screen_y = win32api.GetCursorPos()
        return self.mapFromGlobal(
            QPoint(round(screen_x / self._scaling), round(screen_y / self._scaling))
        )

    def _paint_recording_overlay(
        self,
        painter: QPainter,
        mouse_position: QPoint,
        content: RecordingOverlayContent,
    ) -> None:
        pen = QPen(QColor(0, 255, 180, 220), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(0, mouse_position.y(), self.width(), mouse_position.y())
        painter.drawLine(mouse_position.x(), 0, mouse_position.x(), self.height())

        painter.setPen(QPen(QColor(255, 80, 80, 230), 2))
        for marker in content.markers:
            x = round(marker.x * self.width())
            y = round(marker.y * self.height())
            painter.drawLine(x - 6, y, x + 6, y)
            painter.drawLine(x, y - 6, x, y + 6)
            painter.drawText(x + 8, y - 8, str(marker.index))

        if not content.instruction:
            return
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        padding = 6
        text_rect = metrics.boundingRect(
            QRect(0, 0, min(360, self.width()), max(1, self.height())),
            Qt.TextFlag.TextWordWrap,
            content.instruction,
        )
        box_width = min(max(text_rect.width() + padding * 2, 120), self.width())
        box_height = min(text_rect.height() + padding * 2, self.height())
        offset_x = max(1, round(self.width() * 14 / 1280))
        offset_y = max(1, round(self.height() * 14 / 720))
        box_x = min(max(0, mouse_position.x() + offset_x), max(0, self.width() - box_width))
        box_y = min(max(0, mouse_position.y() + offset_y), max(0, self.height() - box_height))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 170))
        painter.drawRoundedRect(QRectF(box_x, box_y, box_width, box_height), 4, 4)
        painter.setPen(QPen(QColor(255, 255, 255, 235), 1))
        painter.drawText(
            QRectF(
                box_x + padding,
                box_y + padding,
                box_width - padding * 2,
                box_height - padding * 2,
            ),
            Qt.TextFlag.TextWordWrap,
            content.instruction,
        )


def install_overlay_window(parent=None) -> OverlayWindow:
    """Create and bind the application overlay owned by the main window."""

    overlay_window = OverlayWindow(parent)
    communicate.overlay_shown.connect(overlay_window.show_overlay)
    communicate.overlay_cleared.connect(overlay_window.clear_overlay)
    communicate.window.connect(overlay_window.update_capture_geometry)
    if parent is not None:
        parent._overlay_window = overlay_window
    return overlay_window
