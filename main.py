#!/usr/bin/env python3
# sechan-ss -- anti-cheat investigation tool
# built at 3am on a tuesday. it works tho.
# based on chicho ss helper & ultra-ss-tool

import sys
import os
import threading
import ctypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def _elevate():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1
    )
    sys.exit()


if not _is_admin():
    _elevate()

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.theme import load_style, setup_fonts
from ui.main_window import MainWindow
from core.resources import ensure_icons


def main():
    threading.Thread(target=ensure_icons, daemon=True).start()

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(load_style())
    setup_fonts(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
