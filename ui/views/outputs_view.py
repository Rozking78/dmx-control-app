"""
Outputs View - Simplified layout
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt


class OutputsView(QWidget):
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
        header.addWidget(QLabel("OUTPUTS"))
        header.addStretch()

        add_display_btn = QPushButton("+ ADD DISPLAY")
        add_display_btn.clicked.connect(self.add_display)
        header.addWidget(add_display_btn)

        add_btn = QPushButton("+ ADD NDI")
        add_btn.clicked.connect(self.add_ndi)
        header.addWidget(add_btn)

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Outputs list
        self.outputs_list = QListWidget()
        self.outputs_list.itemDoubleClicked.connect(self.edit_output)
        layout.addWidget(self.outputs_list)

        self.refresh()

    def refresh(self):
        self.outputs_list.clear()
        try:
            for output in self.api.get_outputs():
                status = "ON" if output.get('enabled') else "OFF"
                text = f"{output.get('name')}  -  {output.get('type', '').upper()}  -  {status}"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, output)
                self.outputs_list.addItem(item)
        except:
            pass

    def add_ndi(self):
        name, ok = QInputDialog.getText(self, "Add NDI", "Name:")
        if ok and name:
            try:
                self.api.add_ndi_output(name)
                self.refresh()
            except:
                pass

    def add_display(self):
        """Add a physical display output."""
        try:
            displays = self.api.get_displays()
            if not displays:
                QMessageBox.information(self, "No Displays", "No available displays found.")
                return

            # Build list of display names
            display_names = []
            for d in displays:
                name = d.get('name', 'Unknown')
                res = f"{d.get('width', '?')}x{d.get('height', '?')}"
                display_names.append(f"{name} ({res})")

            # Let user pick one
            choice, ok = QInputDialog.getItem(
                self, "Add Display Output", "Select display:",
                display_names, 0, False
            )
            if ok and choice:
                idx = display_names.index(choice)
                display_id = displays[idx].get('id')
                self.api.add_display_output(display_id)
                self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add display: {e}")

    def edit_output(self, item):
        output = item.data(Qt.UserRole)
        if output:
            dlg = OutputDialog(self.api, output, self)
            if dlg.exec_() == QDialog.Accepted:
                self.refresh()


class OutputDialog(QDialog):
    def __init__(self, api, output, parent=None):
        super().__init__(parent)
        self.api = api
        self.output = output
        self.setWindowTitle(output.get('name', 'Output'))
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(12)

        s = self.output.get('settings', {})

        self.x = QSpinBox()
        self.x.setRange(-9999, 9999)
        self.x.setValue(s.get('x', 0))
        form.addRow("X:", self.x)

        self.y = QSpinBox()
        self.y.setRange(-9999, 9999)
        self.y.setValue(s.get('y', 0))
        form.addRow("Y:", self.y)

        self.w = QSpinBox()
        self.w.setRange(1, 9999)
        self.w.setValue(s.get('width', 1920))
        form.addRow("Width:", self.w)

        self.h = QSpinBox()
        self.h.setRange(1, 9999)
        self.h.setValue(s.get('height', 1080))
        form.addRow("Height:", self.h)

        layout.addLayout(form)

        # Buttons
        btns = QHBoxLayout()

        toggle_btn = QPushButton("DISABLE" if self.output.get('enabled') else "ENABLE")
        toggle_btn.clicked.connect(self.toggle)
        btns.addWidget(toggle_btn)

        del_btn = QPushButton("DELETE")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self.delete)
        btns.addWidget(del_btn)

        btns.addStretch()

        save_btn = QPushButton("SAVE")
        save_btn.setObjectName("success")
        save_btn.clicked.connect(self.save)
        btns.addWidget(save_btn)

        layout.addLayout(btns)

    def toggle(self):
        try:
            if self.output.get('enabled'):
                self.api.disable_output(self.output['id'])
            else:
                self.api.enable_output(self.output['id'])
            self.accept()
        except:
            pass

    def delete(self):
        try:
            self.api.delete_output(self.output['id'])
            self.accept()
        except:
            pass

    def save(self):
        try:
            self.api.update_output_settings(self.output['id'], {
                'x': self.x.value(),
                'y': self.y.value(),
                'width': self.w.value(),
                'height': self.h.value(),
            })
            self.accept()
        except:
            pass
