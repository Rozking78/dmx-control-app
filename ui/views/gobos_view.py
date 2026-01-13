"""
Gobos View - Gobo grid management
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton, QSpinBox,
    QFileDialog, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl


class GobosView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.selected_slot = 21
        self.gobo_widgets = {}
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)
        self.pending_loads = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("GOBOS (SLOTS 21-200)")
        title.setObjectName("heading")
        layout.addWidget(title)

        # Upload zone
        upload_frame = QFrame()
        upload_frame.setObjectName("panel")
        upload_frame.setStyleSheet("""
            QFrame#panel {
                border: 2px dashed #ff00cc;
                background: rgba(255, 0, 204, 0.05);
            }
        """)
        upload_layout = QHBoxLayout(upload_frame)

        upload_layout.addWidget(QLabel("Upload gobo to slot:"))

        self.slot_spin = QSpinBox()
        self.slot_spin.setRange(21, 200)
        self.slot_spin.setValue(self.selected_slot)
        self.slot_spin.valueChanged.connect(self.on_slot_changed)
        upload_layout.addWidget(self.slot_spin)

        browse_btn = QPushButton("BROWSE PNG")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff00cc, stop:1 #9900ff);
                color: white;
                border: none;
            }
        """)
        browse_btn.clicked.connect(self.browse_gobo)
        upload_layout.addWidget(browse_btn)

        upload_layout.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.clicked.connect(self.refresh)
        upload_layout.addWidget(refresh_btn)

        layout.addWidget(upload_frame)

        # Gobo grid in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(8)

        # Create grid items (21-200 = 180 slots)
        for i, slot in enumerate(range(21, 201)):
            row = i // 10
            col = i % 10
            item = self.create_gobo_item(slot)
            self.grid_layout.addWidget(item, row, col)
            self.gobo_widgets[slot] = item

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)

        self.refresh()

    def create_gobo_item(self, slot):
        item = QFrame()
        item.setFixedSize(100, 100)
        item.setObjectName("card")
        item.slot = slot

        item_layout = QVBoxLayout(item)
        item_layout.setContentsMargins(4, 4, 4, 4)
        item_layout.setSpacing(2)

        image_label = QLabel()
        image_label.setFixedSize(80, 70)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("background: black; border-radius: 4px;")
        image_label.setText("Empty")
        image_label.setStyleSheet("background: black; color: #808080; font-size: 10px;")
        item_layout.addWidget(image_label, alignment=Qt.AlignCenter)

        slot_label = QLabel(f"#{slot}")
        slot_label.setStyleSheet("color: #9900ff; font-size: 10px;")
        slot_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(slot_label)

        item.image_label = image_label
        item.mousePressEvent = lambda e, s=slot: self.on_item_clicked(s)

        return item

    def on_item_clicked(self, slot):
        self.selected_slot = slot
        self.slot_spin.setValue(slot)

        # Update selection styling
        for s, widget in self.gobo_widgets.items():
            if s == slot:
                widget.setStyleSheet("QFrame { border: 2px solid #00ffff; }")
            else:
                widget.setStyleSheet("")

    def on_slot_changed(self, value):
        self.on_item_clicked(value)

    def browse_gobo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Gobo Image", "",
            "PNG Images (*.png)"
        )
        if file_path:
            self.upload_gobo(file_path)

    def upload_gobo(self, file_path):
        try:
            self.api.upload_gobo(self.selected_slot, file_path)
            # Move to next slot
            if self.selected_slot < 200:
                self.selected_slot += 1
                self.slot_spin.setValue(self.selected_slot)
            self.refresh()
        except Exception as e:
            print(f"Error uploading gobo: {e}")

    def refresh(self):
        try:
            gobos = self.api.get_gobos()

            # Reset all items
            for slot, widget in self.gobo_widgets.items():
                widget.image_label.setPixmap(QPixmap())
                widget.image_label.setText("Empty")
                widget.image_label.setStyleSheet("background: black; color: #808080; font-size: 10px;")
                widget.has_gobo = False

            # Load gobo images
            for gobo in gobos:
                slot = gobo.get('slot')
                if slot and slot in self.gobo_widgets:
                    widget = self.gobo_widgets[slot]
                    widget.has_gobo = True
                    widget.gobo_id = gobo.get('id')
                    widget.image_label.setText("Loading...")

                    # Load image
                    url = QUrl(self.api.get_gobo_image_url(gobo['id']))
                    request = QNetworkRequest(url)
                    reply = self.network_manager.get(request)
                    self.pending_loads[reply] = slot

        except Exception as e:
            print(f"Error refreshing gobos: {e}")

    def on_image_loaded(self, reply):
        slot = self.pending_loads.pop(reply, None)
        if slot is None or reply.error():
            return

        if slot in self.gobo_widgets:
            widget = self.gobo_widgets[slot]
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                scaled = pixmap.scaled(70, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                widget.image_label.setPixmap(scaled)
                widget.image_label.setText("")
                widget.image_label.setStyleSheet("background: black;")
