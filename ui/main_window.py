"""
Main Window - DMX Visualizer Control
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from ui.views.status_view import StatusView
from ui.views.outputs_view import OutputsView
from ui.views.gobos_view import GobosView
from ui.views.media_view import MediaView
from ui.views.ndi_view import NDIView
from ui.views.gamepad_view import GamepadView
from ui.views.settings_view import SettingsView
from core.api_client import APIClient
from core.gamepad_manager import GamepadManager
from core.config_manager import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = ConfigManager()
        self.api = APIClient(self.config.get('server_url', 'http://localhost:8082'))
        self.gamepad = GamepadManager()

        self.init_ui()
        self.load_stylesheet()
        self.setup_gamepad()
        self.start_connection_check()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("DMX Visualizer Control")
        self.setMinimumSize(1280, 800)

        # Hide status bar for more space
        self.statusBar().hide()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Compact header with tabs integrated
        header = self.create_header()
        layout.addWidget(header)

        # Tab widget - takes all remaining space
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(20, 30, 50, 0.8);
                color: #8099b3;
                padding: 12px 24px;
                margin-right: 2px;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: rgba(0, 255, 255, 0.15);
                color: #00ffff;
                border-bottom: 2px solid #00ffff;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(0, 255, 255, 0.08);
            }
        """)
        layout.addWidget(self.tabs)

        # Create views
        self.status_view = StatusView(self.api)
        self.outputs_view = OutputsView(self.api)
        self.gobos_view = GobosView(self.api)
        self.media_view = MediaView(self.api)
        self.ndi_view = NDIView(self.api)
        self.gamepad_view = GamepadView(self.gamepad, self.config)
        self.settings_view = SettingsView(self.api, self.config, self)

        # Add tabs
        self.tabs.addTab(self.status_view, "STATUS")
        self.tabs.addTab(self.outputs_view, "OUTPUTS")
        self.tabs.addTab(self.gobos_view, "GOBOS")
        self.tabs.addTab(self.media_view, "MEDIA")
        self.tabs.addTab(self.ndi_view, "NDI")
        self.tabs.addTab(self.gamepad_view, "GAMEPAD")
        self.tabs.addTab(self.settings_view, "SETTINGS")

    def create_header(self):
        """Create compact header."""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(45)
        header.setStyleSheet("""
            QFrame#header {
                background: rgba(5, 5, 15, 0.95);
                border-bottom: 1px solid #26334d;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        # Title
        title = QLabel("DMX CONTROL")
        title.setStyleSheet("color: #00ffff; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        layout.addStretch()

        # Connection status - compact
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 16px; color: #ff1a4d;")
        layout.addWidget(self.status_indicator)

        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: #808080; font-size: 12px;")
        layout.addWidget(self.status_label)

        return header

    def load_stylesheet(self):
        """Load the Retro theme stylesheet."""
        style_path = os.path.join(
            os.path.dirname(__file__),
            'styles', 'retro_theme.qss'
        )
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())

    def setup_gamepad(self):
        """Set up gamepad input handling."""
        self.gamepad.button_pressed.connect(self.on_gamepad_button)
        self.gamepad.start()

    def on_gamepad_button(self, button, action):
        """Handle gamepad button presses."""
        if action == 'prev_tab':
            self.prev_tab()
        elif action == 'next_tab':
            self.next_tab()
        elif action == 'select':
            self.activate_focused()
        elif action == 'back':
            self.go_back()
        elif action == 'nav_down':
            self.focus_next()
        elif action == 'nav_up':
            self.focus_prev()
        elif action == 'nav_left':
            self.focus_left()
        elif action == 'nav_right':
            self.focus_right()

    def prev_tab(self):
        """Switch to previous tab."""
        current = self.tabs.currentIndex()
        new_index = (current - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(new_index)

    def next_tab(self):
        """Switch to next tab."""
        current = self.tabs.currentIndex()
        new_index = (current + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(new_index)

    def activate_focused(self):
        """Activate the currently focused widget."""
        focused = self.focusWidget()
        if focused and hasattr(focused, 'click'):
            focused.click()

    def go_back(self):
        """Go back / close dialogs."""
        pass

    def focus_next(self):
        """Move focus down."""
        self._navigate_focus('down')

    def focus_prev(self):
        """Move focus up."""
        self._navigate_focus('up')

    def focus_left(self):
        """Move focus left."""
        self._navigate_focus('left')

    def focus_right(self):
        """Move focus right."""
        self._navigate_focus('right')

    def _navigate_focus(self, direction):
        """Navigate focus in a spatial direction."""
        current = self.focusWidget()
        if not current:
            # No focus, focus first widget
            self.focusNextChild()
            return

        # Get current widget's screen position
        current_rect = current.rect()
        current_pos = current.mapToGlobal(current_rect.center())

        # Find all focusable widgets
        focusable = []
        for widget in self.findChildren(QWidget):
            if (widget.isVisible() and
                widget.isEnabled() and
                widget.focusPolicy() != Qt.NoFocus and
                widget != current):
                focusable.append(widget)

        if not focusable:
            return

        # Find best candidate in the direction
        best = None
        best_score = float('inf')

        for widget in focusable:
            widget_rect = widget.rect()
            widget_pos = widget.mapToGlobal(widget_rect.center())

            dx = widget_pos.x() - current_pos.x()
            dy = widget_pos.y() - current_pos.y()

            # Check if widget is in the right direction
            in_direction = False
            if direction == 'down' and dy > 20:
                in_direction = True
                # Prefer widgets directly below (small dx)
                score = dy + abs(dx) * 2
            elif direction == 'up' and dy < -20:
                in_direction = True
                score = -dy + abs(dx) * 2
            elif direction == 'right' and dx > 20:
                in_direction = True
                score = dx + abs(dy) * 2
            elif direction == 'left' and dx < -20:
                in_direction = True
                score = -dx + abs(dy) * 2

            if in_direction and score < best_score:
                best_score = score
                best = widget

        if best:
            best.setFocus()

    def start_connection_check(self):
        """Start periodic connection checking."""
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(5000)
        self.check_connection()

    def check_connection(self):
        """Check connection to DMX Visualizer."""
        try:
            status = self.api.get_status()
            self.set_connected(True)
        except Exception:
            self.set_connected(False)

    def set_connected(self, connected):
        """Update connection status display."""
        if connected:
            self.status_indicator.setStyleSheet("font-size: 16px; color: #33ff66;")
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #33ff66; font-size: 12px;")
        else:
            self.status_indicator.setStyleSheet("font-size: 16px; color: #ff1a4d;")
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: #808080; font-size: 12px;")

    def keyPressEvent(self, event):
        """Handle keyboard input for testing."""
        if event.key() == Qt.Key_Left and event.modifiers() == Qt.ControlModifier:
            self.prev_tab()
        elif event.key() == Qt.Key_Right and event.modifiers() == Qt.ControlModifier:
            self.next_tab()
        elif event.key() == Qt.Key_Down:
            self.focus_next()
        elif event.key() == Qt.Key_Up:
            self.focus_prev()
        elif event.key() == Qt.Key_Left:
            self.focus_left()
        elif event.key() == Qt.Key_Right:
            self.focus_right()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Space:
            self.activate_focused()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Clean up on close."""
        self.gamepad.stop()
        self.connection_timer.stop()
        event.accept()
