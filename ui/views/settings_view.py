"""
Settings View - Simplified layout
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt


class SettingsView(QWidget):
    def __init__(self, api, config_manager, main_window=None):
        super().__init__()
        self.api = api
        self.config = config_manager
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)

        # Server URL
        layout.addWidget(QLabel("SERVER URL"))

        url_row = QHBoxLayout()
        self.server_url = QLineEdit()
        self.server_url.setPlaceholderText("http://192.168.1.100:8082")
        url_row.addWidget(self.server_url, 1)

        test_btn = QPushButton("TEST")
        test_btn.clicked.connect(self.test_connection)
        url_row.addWidget(test_btn)
        layout.addLayout(url_row)

        # Options
        layout.addWidget(QLabel("OPTIONS"))

        self.auto_connect = QCheckBox("Auto-connect on startup")
        layout.addWidget(self.auto_connect)

        self.fullscreen = QCheckBox("Start fullscreen")
        layout.addWidget(self.fullscreen)

        self.gamepad_enabled = QCheckBox("Enable gamepad input")
        layout.addWidget(self.gamepad_enabled)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        reset_btn = QPushButton("RESET DEFAULTS")
        reset_btn.clicked.connect(self.reset_defaults)
        btn_row.addWidget(reset_btn)

        save_btn = QPushButton("SAVE")
        save_btn.setObjectName("success")
        save_btn.clicked.connect(self.save_settings)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def load_settings(self):
        s = self.config.get_app_settings()
        self.server_url.setText(s.get('server_url', 'http://localhost:8082'))
        self.auto_connect.setChecked(s.get('auto_connect', True))
        self.fullscreen.setChecked(s.get('fullscreen', False))
        self.gamepad_enabled.setChecked(s.get('gamepad_enabled', True))

    def save_settings(self):
        self.config.save_app_settings({
            'server_url': self.server_url.text(),
            'auto_connect': self.auto_connect.isChecked(),
            'fullscreen': self.fullscreen.isChecked(),
            'gamepad_enabled': self.gamepad_enabled.isChecked(),
        })
        self.api.set_base_url(self.server_url.text())
        QMessageBox.information(self, "Saved", "Settings saved.")

    def reset_defaults(self):
        self.config.reset_app_settings()
        self.load_settings()

    def test_connection(self):
        self.api.set_base_url(self.server_url.text())
        try:
            status = self.api.get_status()
            QMessageBox.information(self, "Success", f"Connected!\nVersion: {status.get('version', '?')}")
        except Exception as e:
            QMessageBox.warning(self, "Failed", f"Could not connect:\n{e}")
