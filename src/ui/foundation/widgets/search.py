"""Reusable search-oriented widgets."""

from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QStringListModel, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QCompleter, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    EditableComboBox,
    FluentIcon,
    FluentIconBase,
    IconWidget,
    ListWidget,
    SearchLineEdit,
)


class SearchableComboBox(EditableComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_items = []
        completer = QCompleter(self)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._search_model = QStringListModel(self.search_items, completer)
        completer.setModel(self._search_model)
        self.setCompleter(completer)

    def addItem(
        self, text: str, icon: QIcon | str | FluentIconBase | None = None, userData: Any = None
    ):
        self.search_items.append(text)
        self._search_model.setStringList(self.search_items)
        super().addItem(text, icon, userData)

    def clear(self):
        self.search_items.clear()
        self._search_model.setStringList(self.search_items)
        super().clear()


class SearchableListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.search_edit = SearchLineEdit(self)
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search_edit)
        self.list_widget = ListWidget(self)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def setPlaceholderText(self, text: str):
        self.search_edit.setPlaceholderText(text)

    def setFixedWidth(self, width: int):
        super().setFixedWidth(width)
        self.list_widget.setFixedWidth(width)
        self.search_edit.setFixedWidth(width)

    def _apply_filter(self, keyword: str):
        normalized = keyword.strip().lower()
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            item.setHidden(normalized not in item.text().lower())

    def reapply_filter(self):
        self._apply_filter(self.search_edit.text())

    def __getattr__(self, name):
        if hasattr(self.list_widget, name):
            return getattr(self.list_widget, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class SmoothSearchBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(35)
        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.icon_label = IconWidget(FluentIcon.SEARCH, self)
        self.icon_label.setFixedSize(15, 15)
        self.search_edit = SearchLineEdit(self)
        self.search_edit.setFixedWidth(0)
        self.layout().addWidget(self.search_edit)
        self.layout().addWidget(self.icon_label)
        self.setMouseTracking(True)
        self.icon_label_anim = QPropertyAnimation(self.icon_label, b"maximumWidth")
        self.icon_label_anim.finished.connect(self._on_icon_anim_finished)
        self.should_hide_icon = False
        self.textChanged = self.search_edit.textChanged

    def _on_icon_anim_finished(self):
        if self.should_hide_icon:
            self.icon_label.hide()

    def enterEvent(self, event):
        if self.search_edit.text():
            super().enterEvent(event)
            return
        self.should_hide_icon = True
        self.icon_label_anim.stop()
        self.icon_label_anim.setDuration(100)
        self.icon_label_anim.setStartValue(self.icon_label.width())
        self.icon_label_anim.setEndValue(0)
        self.anim = QPropertyAnimation(self.search_edit, b"maximumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.search_edit.width())
        self.anim.setEndValue(220)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.icon_label_anim.start()
        self.anim.start()
        self.search_edit.setFocus()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.search_edit.text():
            self.should_hide_icon = False
            if hasattr(self, "anim"):
                self.anim.stop()
            self.icon_label_anim.stop()
            self.anim = QPropertyAnimation(self.search_edit, b"maximumWidth")
            self.anim.setDuration(300)
            self.anim.setStartValue(self.search_edit.width())
            self.anim.setEndValue(0)
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.icon_label.show()
            self.icon_label.setMaximumWidth(15)
            self.anim.start()
            self.search_edit.clearFocus()
        super().leaveEvent(event)
