"""
Status View - System status and live preview
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl


class StatusView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.init_ui()
        self.start_updates()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("STATUS")
        title.setObjectName("heading")
        layout.addWidget(title)

        # Status cards
        cards_frame = QFrame()
        cards_frame.setObjectName("panel")
        cards_layout = QHBoxLayout(cards_frame)
        cards_layout.setSpacing(30)

        self.status_cards = {}
        for key, label in [
            ('version', 'VERSION'),
            ('fixtures', 'FIXTURES'),
            ('resolution', 'RESOLUTION'),
            ('outputs', 'OUTPUTS'),
            ('fps', 'FPS'),
        ]:
            card = self.create_status_card(label)
            cards_layout.addWidget(card)
            self.status_cards[key] = card

        layout.addWidget(cards_frame)

        # Preview section
        preview_frame = QFrame()
        preview_frame.setObjectName("panel")
        preview_layout = QVBoxLayout(preview_frame)

        preview_title = QLabel("LIVE PREVIEW")
        preview_title.setObjectName("subheading")
        preview_layout.addWidget(preview_title)

        self.preview_label = QLabel("Connecting...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setStyleSheet("""
            background: black;
            border: 2px solid #00ffff;
            border-radius: 8px;
        """)
        preview_layout.addWidget(self.preview_label)

        layout.addWidget(preview_frame)
        layout.addStretch()

        # Network manager for preview images
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_preview_loaded)

    def create_status_card(self, label):
        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setObjectName("secondary")
        card_layout.addWidget(label_widget)

        value_widget = QLabel("-")
        value_widget.setObjectName("value")
        value_widget.setStyleSheet("font-size: 24px;")
        card_layout.addWidget(value_widget)

        card.value_label = value_widget
        return card

    def start_updates(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)

        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
        self.preview_timer.start(100)  # 10 FPS preview

        self.update_status()

    def update_status(self):
        try:
            status = self.api.get_status()
            self.status_cards['version'].value_label.setText(status.get('version', '-'))
            self.status_cards['fixtures'].value_label.setText(str(status.get('fixtures', 0)))
            self.status_cards['resolution'].value_label.setText(status.get('resolution', '-'))
            self.status_cards['outputs'].value_label.setText(str(status.get('outputCount', 0)))
            self.status_cards['fps'].value_label.setText(str(status.get('fps', 0)))
        except Exception:
            pass

    def update_preview(self):
        try:
            url = QUrl(self.api.get_preview_url())
            request = QNetworkRequest(url)
            self.network_manager.get(request)
        except Exception:
            pass

    def on_preview_loaded(self, reply):
        if reply.error():
            return

        data = reply.readAll()
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            scaled = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
