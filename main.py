#!/usr/bin/env python3
"""
DMX Visualizer Control - Steam Deck Remote Control App
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

from ui.main_window import MainWindow


def load_fonts():
    """Load custom fonts for the Retro theme."""
    fonts_dir = os.path.join(os.path.dirname(__file__), 'resources', 'fonts')
    if os.path.exists(fonts_dir):
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith(('.ttf', '.otf')):
                QFontDatabase.addApplicationFont(os.path.join(fonts_dir, font_file))


def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("DMX Visualizer Control")
    app.setOrganizationName("GeoDraw")

    # Load custom fonts
    load_fonts()

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
