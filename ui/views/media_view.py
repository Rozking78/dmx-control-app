"""
Media View - Simplified layout
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt


class MediaView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("MEDIA (Slots 201-255)"))
        header.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Upload buttons
        upload_row = QHBoxLayout()

        video_btn = QPushButton("UPLOAD VIDEO")
        video_btn.clicked.connect(self.upload_video)
        upload_row.addWidget(video_btn)

        image_btn = QPushButton("UPLOAD IMAGE")
        image_btn.clicked.connect(self.upload_image)
        upload_row.addWidget(image_btn)

        layout.addLayout(upload_row)

        # Media list
        layout.addWidget(QLabel("UPLOADED MEDIA"))
        self.media_list = QListWidget()
        layout.addWidget(self.media_list)

        self.refresh()

    def refresh(self):
        self.media_list.clear()
        try:
            for v in self.api.get_videos():
                item = QListWidgetItem(f"VIDEO: {v.get('name')}")
                self.media_list.addItem(item)
            for i in self.api.get_images():
                item = QListWidgetItem(f"IMAGE: {i.get('name')}")
                self.media_list.addItem(item)
        except:
            pass

    def upload_video(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Videos", "", "Video (*.mp4 *.mov *.avi *.mkv)"
        )
        for f in files:
            try:
                self.api.upload_video(f)
            except:
                pass
        self.refresh()

    def upload_image(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.gif)"
        )
        for f in files:
            try:
                self.api.upload_image(f)
            except:
                pass
        self.refresh()
