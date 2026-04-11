from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from qfluentwidgets import (BodyLabel, CardWidget, FluentIcon,
                            ImageLabel, MessageBoxBase,
                            PrimaryPushButton, SubtitleLabel)

from ok import og
from ok.gui.widget.CustomTab import CustomTab
from src.char.custom.CustomCharManager import CustomCharManager
from src.tasks.trigger.AutoCombatTask import AutoCombatTask, scanner_signals
from src.ui.common import char_manager_signals, cv_to_pixmap, SearchableComboBox


class NewCharDialog(MessageBoxBase):

    def __init__(self, mat, manager: CustomCharManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.tr_title = og.app.tr("记录新特征")
        self.tr_name_ph = og.app.tr("输入或选择关联的角色名称")
        self.tr_list_ph = og.app.tr("输入或选择绑定的出招表 (可选)")

        self.viewLayout.setSpacing(10)
        self.viewLayout.addWidget(SubtitleLabel(self.tr_title, self), alignment=Qt.AlignmentFlag.AlignCenter)

        img_label = ImageLabel()
        img_label.setImage(cv_to_pixmap(mat).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.viewLayout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 提示现有的角色列表
        self.existing_chars = list(self.manager.get_all_characters().keys())
        # To do a simple dropdown for existing, combining ComboBox
        self.char_combo = SearchableComboBox()
        self.char_combo.setPlaceholderText(self.tr_name_ph)
        self.char_combo.addItems([""] + self.existing_chars)
        self.char_combo.currentTextChanged.connect(self._on_char_select)
        self.viewLayout.addWidget(self.char_combo)

        self.combo_list = SearchableComboBox()
        self.combo_list.setPlaceholderText(self.tr_list_ph)
        self.combo_list.addItem("", userData="")
        for label, combo_ref in self.manager.get_all_combo_items():
            self.combo_list.addItem(label, userData=combo_ref)
        self.viewLayout.addWidget(self.combo_list)

        self.widget.setMinimumWidth(320)

    def _on_char_select(self, text):
        if not text:
            return
        char_info = self.manager.get_character_info(text)
        combo_value = char_info.get("combo_ref", "") if isinstance(char_info, dict) else ""
        if combo_value:
            combo_ref = self.manager.to_combo_ref(combo_value)
            idx = self.combo_list.findData(combo_ref)
            if idx >= 0:
                self.combo_list.setCurrentIndex(idx)
            else:
                self.combo_list.setCurrentText(self.manager.to_combo_label(combo_ref))
        elif isinstance(char_info, dict):
            self.combo_list.setCurrentIndex(0)

    def get_data(self):
        char_name = self.char_combo.currentText().strip()
        combo_label = self.combo_list.currentText().strip()
        combo_ref = self.manager.to_combo_ref(combo_label)
        idx = self.combo_list.currentIndex()
        if idx >= 0 and combo_label == self.combo_list.itemText(idx):
            data = self.combo_list.itemData(idx)
            if isinstance(data, str):
                combo_ref = data
        return char_name, combo_ref


class SlotCard(CardWidget):

    def __init__(self, index, manager: CustomCharManager, parent=None):
        super().__init__(parent)
        self.index = index
        self.manager = manager
        self.tr_match_success = og.app.tr("匹配成功: {}")
        self.tr_unrecognized = og.app.tr("未能识别该特征")
        self.tr_no_image = og.app.tr("无画面")
        self.tr_dlg_title = og.app.tr("记录新特征")
        self.tr_slot_title = og.app.tr("{} 号位")
        self.tr_scan_prompt = og.app.tr("点击上方按钮扫描...")
        self.tr_action_btn = og.app.tr("未识别，关联新特征")

        self.vbox = QVBoxLayout(self)
        self.title = SubtitleLabel(self.tr_slot_title.format(index + 1))
        self.image = ImageLabel()
        self.image.setFixedSize(120, 120)
        self.status = BodyLabel(self.tr_scan_prompt)
        self.btn_act = PrimaryPushButton(self.tr_action_btn, self)
        self.btn_act.hide()

        self.vbox.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vbox.addWidget(self.image, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vbox.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vbox.addWidget(self.btn_act, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_act.clicked.connect(self.on_action)
        self.current_mat = None
        self.current_w = 0
        self.current_h = 0

    def update_result(self, mat, w, h, match_name):
        self.current_mat = mat
        self.current_w = w
        self.current_h = h
        if mat is not None and getattr(mat, 'size', 0) > 0:
            pixmap = cv_to_pixmap(mat)
            self.image.setImage(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.image.setImage(QPixmap())

        if match_name:
            self.status.setText(self.tr_match_success.format(match_name))
            self.btn_act.hide()
        elif mat is not None:
            self.status.setText(self.tr_unrecognized)
            self.btn_act.show()
        else:
            self.status.setText(self.tr_no_image)
            self.btn_act.hide()

    def on_action(self):
        dialog = NewCharDialog(self.current_mat, self.manager, self.window())
        if dialog.exec():
            char_name, combo_ref = dialog.get_data()
            if char_name and self.current_mat is not None:
                self.manager.add_feature_to_character(char_name, self.current_mat, width=self.current_w, height=self.current_h)
                self.manager.add_character(char_name, combo_ref)
                if not self.manager.is_custom_combo_exist(combo_ref):
                    self.manager.add_combo(combo_ref, "")
                self.update_result(self.current_mat, self.current_w, self.current_h, char_name)
                char_manager_signals.refresh_tab.emit()


class TeamScannerTab(CustomTab):

    def __init__(self, manager: CustomCharManager = None):
        super().__init__()
        self.tr_scan_btn = og.app.tr("扫描当前队伍屏幕槽位")
        self.tr_scanning = og.app.tr("扫描中...")
        self.tr_analyzing = og.app.tr("正在分析...")
        self.tr_no_feature = og.app.tr("未获取到特征")
        self.tr_name_tab = og.app.tr("扫描队伍")
        # self.tr_header = og.app.tr("队伍角色扫描")
        self.tr_desc = og.app.tr("未识别也可自动战斗，将使用通用脚本(BaseChar)")

        self.manager = manager or CustomCharManager()
        self.icon = FluentIcon.CAMERA
        self.logger.info("Init TeamScannerTab")

        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.setSpacing(20)

        # Header
        # self.header = SubtitleLabel(self.tr_header)
        self.scan_btn = PrimaryPushButton(FluentIcon.SYNC, self.tr_scan_btn)
        self.scan_btn.setFixedWidth(250)
        self.scan_btn.clicked.connect(self.on_scan_clicked)

        # self.vbox.addWidget(self.header)
        self.vbox.addWidget(self.scan_btn)

        # Cards Layout
        self.cards_layout = QHBoxLayout()
        self.slots: list[SlotCard] = []
        for i in range(4):
            card = SlotCard(i, self.manager, self)
            self.slots.append(card)
            self.cards_layout.addWidget(card)

        self.vbox.addLayout(self.cards_layout)

        self.desc = BodyLabel(self.tr_desc)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vbox.addWidget(self.desc)

        self.vbox.addStretch(1)

        # Connect Signal
        scanner_signals.scan_done.connect(self.on_scan_done)

    @property
    def name(self):
        return self.tr_name_tab

    def on_scan_clicked(self):
        og.app.start_controller.handler.post(self.scan_team)

    def scan_team(self):
        og.app.start_controller.do_start()
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText(self.tr_scanning)
        for card in self.slots:
            card.status.setText(self.tr_analyzing)
            card.btn_act.hide()
        self.get_task(AutoCombatTask).scan_team()

    def on_scan_done(self, results):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText(self.tr_scan_btn)

        if not results:
            for card in self.slots:
                card.status.setText(self.tr_no_feature)
            return

        updated_indices = set()
        for res in results:
            idx = res.get("index")
            mat = res.get("mat")
            w = res.get("width", 0)
            h = res.get("height", 0)
            match_name = res.get("match")
            if 0 <= idx < 4:
                self.slots[idx].update_result(mat, w, h, match_name)
                updated_indices.add(idx)

        for i in range(4):
            if i not in updated_indices:
                self.slots[i].update_result(None, 0, 0, "")
                self.slots[i].status.setText(self.tr_no_feature)
