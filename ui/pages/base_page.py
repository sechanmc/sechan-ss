from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from ..widgets import ScanOutputWidget
from ..theme import Colors


class BasePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")

    def _build(self, title, subtitle, scan_cb):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # header
        hdr = QFrame()
        hdr.setStyleSheet(f"background-color: #252526; border-bottom: 1px solid {Colors.BORDER};")
        hdr.setFixedHeight(44)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(8)

        indent = QFrame()
        indent.setFixedSize(3, 20)
        indent.setStyleSheet("background-color: #569cd6;")
        hl.addWidget(indent)

        t = QLabel(f"$ {title}")
        t.setStyleSheet("color: #d4d4d4; font-size: 14px; font-weight: bold; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        hl.addWidget(t)
        hl.addStretch()

        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; background: transparent;")
        hl.addWidget(s)

        layout.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.scan_btn = QPushButton("run scan")
        self.scan_btn.setObjectName("primaryButton")
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_btn.setMinimumHeight(32)
        self.scan_btn.clicked.connect(scan_cb)

        self.clear_btn = QPushButton("clear")
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setMinimumHeight(32)
        self.clear_btn.clicked.connect(self._clear)

        btn_row.addWidget(self.scan_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

        self.status = QLabel("ready")
        self.status.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; padding: 2px 0; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        cl.addWidget(self.status)

        self.output = ScanOutputWidget()
        cl.addWidget(self.output, 1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    def _clear(self):
        self.output.clear_output()
        self.status.setText("ready")

    def _busy(self, busy):
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(not busy)
            self.scan_btn.setText("scanning..." if busy else "run scan")
        self.status.setText("scanning..." if busy else "done")
