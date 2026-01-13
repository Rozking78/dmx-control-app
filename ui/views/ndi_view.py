"""
NDI View - NDI source discovery and management
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QListWidget, QListWidgetItem, QPushButton
)
from PyQt5.QtCore import Qt


class NDIView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("NDI SOURCES")
        title.setObjectName("heading")
        layout.addWidget(title)

        # Refresh button
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("REFRESH SOURCES")
        self.refresh_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self.refresh_sources)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Sources list
        self.sources_list = QListWidget()
        layout.addWidget(self.sources_list)

        # Info panel
        info_frame = QFrame()
        info_frame.setObjectName("panel")
        info_layout = QVBoxLayout(info_frame)

        info_title = QLabel("NDI INFO")
        info_title.setObjectName("subheading")
        info_layout.addWidget(info_title)

        info_text = QLabel("""
NDI (Network Device Interface) allows video to be sent over your local network.

• Sources are auto-discovered on your network
• Click Refresh to scan for new sources
• Use Output settings to add NDI outputs
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: rgb(128, 153, 179);")
        info_layout.addWidget(info_text)

        layout.addWidget(info_frame)
        layout.addStretch()

        self.refresh()

    def refresh(self):
        self.sources_list.clear()

        try:
            sources = self.api.get_ndi_sources()

            if not sources:
                item = QListWidgetItem("No NDI sources found. Click Refresh to discover.")
                item.setForeground(Qt.gray)
                self.sources_list.addItem(item)
                return

            for source in sources:
                item = QListWidgetItem()
                item.setData(Qt.UserRole, source)

                name = source.get('name', 'Unknown')
                address = source.get('address', 'Auto-discovered')
                connected = source.get('connected', False)

                status = "CONNECTED" if connected else "AVAILABLE"
                text = f"{name}\n{address} | {status}"
                item.setText(text)

                self.sources_list.addItem(item)

        except Exception as e:
            item = QListWidgetItem(f"Error: {e}")
            item.setForeground(Qt.red)
            self.sources_list.addItem(item)

    def refresh_sources(self):
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("REFRESHING...")

        try:
            self.api.refresh_ndi_sources()
            # Wait a moment for discovery
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, self.on_refresh_complete)
        except Exception as e:
            print(f"Error refreshing NDI: {e}")
            self.on_refresh_complete()

    def on_refresh_complete(self):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("REFRESH SOURCES")
        self.refresh()
