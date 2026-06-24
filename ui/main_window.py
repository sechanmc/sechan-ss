from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer
import os

from .theme import Colors
from .widgets import SidebarButton, Toast
from .pages.dashboard import DashboardPage
from .pages.appdata_scan import AppDataScanPage
from .pages.process_scan import ProcessScanPage
from .pages.minecraft_scan import MinecraftScanPage
from .pages.system_scan import SystemScanPage
from .pages.launcher_scan import LauncherScanPage
from .pages.browser_forensics import BrowserForensicsPage
from .pages.settings import SettingsPage
from core.resources import get_icons


PAGES = [
    ("dashboard",      "dashboard", 0),
    ("appdata",        "appdata",   1),
    ("processes",      "process",   2),
    ("minecraft",      "minecraft", 3),
    ("system",         "system",    4),
    ("launchers",      "launcher",  5),
    ("browser",        "browser",   6),
    ("settings",       "settings",  7),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("sechan-ss :: anti-cheat tool")
        self.setMinimumSize(1100, 700)
        self.resize(1350, 800)

        self.icons = get_icons()
        self._setup()

    def _setup(self):
        c = QWidget()
        self.setCentralWidget(c)
        ml = QHBoxLayout(c)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        # sidebar
        sb = QFrame()
        sb.setObjectName("sidebar")
        sb.setFixedWidth(180)
        sbl = QVBoxLayout(sb)
        sbl.setContentsMargins(0, 0, 0, 0)
        sbl.setSpacing(0)

        # brand line
        br = QFrame()
        br.setFixedHeight(36)
        br.setStyleSheet(f"background-color: #252526; border-bottom: 1px solid {Colors.BORDER};")
        brl = QHBoxLayout(br)
        brl.setContentsMargins(10, 0, 10, 0)
        b = QLabel("sechan-ss")
        b.setStyleSheet("color: #569cd6; font-size: 12px; font-weight: bold; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        brl.addWidget(b)
        brl.addStretch()
        sbl.addWidget(br)

        self.btns = []
        for name, ick, idx in PAGES:
            ip = self.icons.get(ick)
            btn = SidebarButton(name, ip)
            btn.clicked.connect(lambda checked, i=idx: self._go(i))
            sbl.addWidget(btn)
            self.btns.append(btn)

        sbl.addStretch()

        f = QLabel("  v2  |  2026")
        f.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 10px; padding: 6px 10px; background: transparent;")
        sbl.addWidget(f)

        # content
        cx = QFrame()
        cx.setObjectName("contentArea")
        cxl = QVBoxLayout(cx)
        cxl.setContentsMargins(0, 0, 0, 0)
        cxl.setSpacing(0)

        self.stack = QStackedWidget()
        pages = [
            (DashboardPage, 0), (AppDataScanPage, 1), (ProcessScanPage, 2),
            (MinecraftScanPage, 3), (SystemScanPage, 4), (LauncherScanPage, 5),
            (BrowserForensicsPage, 6), (SettingsPage, 7),
        ]
        self.page_map = {}
        for cls, idx in pages:
            p = cls(self)
            self.page_map[idx] = p
            self.stack.addWidget(p)

        cxl.addWidget(self.stack)
        ml.addWidget(sb)
        ml.addWidget(cx, 1)

        self.btns[0].setChecked(True)

    def _go(self, idx):
        for i, b in enumerate(self.btns):
            b.setChecked(i == idx)
        self.stack.setCurrentIndex(idx)

    def _toast(self, msg, type_="info", dur=4000):
        Toast(self, msg, type_, dur).show()
        self._repos()

    def _repos(self):
        ts = self.findChildren(Toast)
        y = 10
        for t in ts:
            t.move(self.width() - t.width() - 10, y)
            y += t.height() + 4

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._repos()

    def show_toast(self, msg, type_="info", dur=4000):
        self._toast(msg, type_, dur)
