"""
Gamepad View - Simplified layout
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QListWidget, QListWidgetItem, QPushButton,
    QComboBox, QSlider, QCheckBox, QScrollArea,
    QInputDialog, QFileDialog
)
from PyQt5.QtCore import Qt

from core.gamepad_manager import AVAILABLE_ACTIONS, BUTTON_NAMES


class GamepadView(QWidget):
    def __init__(self, gamepad_manager, config_manager):
        super().__init__()
        self.gamepad = gamepad_manager
        self.config = config_manager
        self.button_combos = {}
        self.init_ui()
        self.setup_signals()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # LEFT: Profiles
        left = QVBoxLayout()
        left.setSpacing(16)

        # Status
        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #ff1a4d; font-size: 24px;")
        status_row.addWidget(self.status_dot)
        self.status_text = QLabel("No gamepad")
        status_row.addWidget(self.status_text)
        status_row.addStretch()
        left.addLayout(status_row)

        left.addWidget(QLabel("PROFILES"))

        self.profiles_list = QListWidget()
        self.profiles_list.setMaximumHeight(200)
        self.profiles_list.currentItemChanged.connect(self.on_profile_selected)
        left.addWidget(self.profiles_list)

        btn_row = QHBoxLayout()
        new_btn = QPushButton("NEW")
        new_btn.clicked.connect(self.new_profile)
        btn_row.addWidget(new_btn)
        del_btn = QPushButton("DELETE")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self.delete_profile)
        btn_row.addWidget(del_btn)
        left.addLayout(btn_row)

        save_btn = QPushButton("SAVE PROFILE")
        save_btn.setObjectName("success")
        save_btn.clicked.connect(self.save_profile)
        left.addWidget(save_btn)

        left.addStretch()
        layout.addLayout(left, 1)

        # RIGHT: Mappings (scrollable)
        right = QVBoxLayout()
        right.addWidget(QLabel("BUTTON MAPPINGS"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)

        for btn_id, btn_name in BUTTON_NAMES.items():
            row = QHBoxLayout()

            label = QLabel(f"{btn_name}")
            label.setStyleSheet("color: #00ffff; min-width: 80px;")
            row.addWidget(label)

            combo = QComboBox()
            for action_id, action_name in AVAILABLE_ACTIONS.items():
                combo.addItem(action_name, action_id)

            current = self.gamepad.get_mapping(btn_id)
            idx = combo.findData(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)

            combo.currentIndexChanged.connect(
                lambda i, b=btn_id, c=combo: self.on_mapping_changed(b, c)
            )
            row.addWidget(combo, 1)

            self.button_combos[btn_id] = combo
            scroll_layout.addLayout(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        right.addWidget(scroll)

        layout.addLayout(right, 2)

        self.refresh_profiles()
        self.refresh_status()

    def setup_signals(self):
        self.gamepad.gamepad_connected.connect(self.on_connected)
        self.gamepad.gamepad_disconnected.connect(self.on_disconnected)

    def refresh_profiles(self):
        self.profiles_list.clear()
        for name in self.config.get_profile_list():
            item = QListWidgetItem(name.title())
            item.setData(Qt.UserRole, name)
            if name == self.config.get_active_profile():
                item.setText(f"● {name.title()}")
            self.profiles_list.addItem(item)

    def refresh_status(self):
        if self.gamepad.is_connected():
            self.on_connected(self.gamepad.get_gamepad_name())
        else:
            self.on_disconnected()

    def on_connected(self, name):
        self.status_dot.setStyleSheet("color: #33ff66; font-size: 24px;")
        self.status_text.setText(name)

    def on_disconnected(self):
        self.status_dot.setStyleSheet("color: #ff1a4d; font-size: 24px;")
        self.status_text.setText("No gamepad")

    def on_profile_selected(self, item):
        if item:
            profile = self.config.get_gamepad_profile(item.data(Qt.UserRole))
            if profile:
                buttons = profile.get('buttons', {})
                for btn_id, combo in self.button_combos.items():
                    action = buttons.get(str(btn_id), 'none')
                    idx = combo.findData(action)
                    if idx >= 0:
                        combo.setCurrentIndex(idx)

    def on_mapping_changed(self, btn_id, combo):
        self.gamepad.set_mapping(btn_id, combo.currentData())

    def new_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Name:")
        if ok and name:
            self.gamepad.save_profile(name.lower().replace(' ', '_'))
            self.refresh_profiles()

    def delete_profile(self):
        item = self.profiles_list.currentItem()
        if item and self.config.delete_gamepad_profile(item.data(Qt.UserRole)):
            self.refresh_profiles()

    def save_profile(self):
        item = self.profiles_list.currentItem()
        if item:
            name = item.data(Qt.UserRole)
            self.gamepad.save_profile(name)
            self.config.set_active_profile(name)
            self.refresh_profiles()
