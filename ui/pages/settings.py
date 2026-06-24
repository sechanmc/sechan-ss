from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt
from ..widgets import Card
from ..theme import Colors
from .base_page import BasePage


class SettingsPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw

        # init webhook storage on main window if not present
        if not hasattr(self.mw, 'webhook_url'):
            self.mw.webhook_url = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

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
        t = QLabel("$ settings")
        t.setStyleSheet("color: #d4d4d4; font-size: 14px; font-weight: bold; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        hl.addWidget(t)
        hl.addStretch()
        layout.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(8)

        # webhook
        wc = Card()
        wt = QLabel("# webhook")
        wt.setObjectName("cardTitle")
        wc.layout().addWidget(wt)
        wd = QLabel("discord webhook url. leave empty to disable auto-reporting.")
        wd.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        wd.setWordWrap(True)
        wc.layout().addWidget(wd)

        wr = QHBoxLayout()
        wr.setSpacing(6)
        self.wh = QLineEdit()
        self.wh.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.wh.setText(self.mw.webhook_url)
        wr.addWidget(self.wh, 1)
        save = QPushButton("save")
        save.setObjectName("successButton")
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.setMinimumHeight(30)
        save.clicked.connect(self._save)
        wr.addWidget(save)
        wc.layout().addLayout(wr)

        test = QPushButton("test webhook")
        test.setCursor(Qt.CursorShape.PointingHandCursor)
        test.setMinimumHeight(30)
        test.clicked.connect(self._test)
        wc.layout().addWidget(test)

        cl.addWidget(wc)

        # options
        oc = Card()
        ot = QLabel("# options")
        ot.setObjectName("cardTitle")
        oc.layout().addWidget(ot)
        self.admin_cb = QCheckBox("relaunch as admin when needed")
        self.admin_cb.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; spacing: 6px; font-size: 12px;")
        self.admin_cb.setChecked(True)
        oc.layout().addWidget(self.admin_cb)
        self.webhook_cb = QCheckBox("send scan results to webhook")
        self.webhook_cb.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; spacing: 6px; font-size: 12px;")
        self.webhook_cb.setChecked(bool(self.mw.webhook_url))
        oc.layout().addWidget(self.webhook_cb)
        cl.addWidget(oc)

        # about
        ac = Card()
        at = QLabel("# about")
        at.setObjectName("cardTitle")
        ac.layout().addWidget(at)
        lines = [
            "sechan-ss v2",
            "pyside6 + pyinstaller",
            "based on chicho ss helper & ultra-ss-tool",
            "",
            "reports saved to: ~/Documents/sechan-ss/reports/",
            "",
            "use responsibly. anti-cheat investigation tool.",
        ]
        for line in lines:
            lb = QLabel(line)
            if line:
                lb.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
            lb.setWordWrap(True)
            ac.layout().addWidget(lb)
        cl.addWidget(ac)
        cl.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    def _save(self):
        url = self.wh.text().strip()
        self.mw.webhook_url = url
        self.webhook_cb.setChecked(bool(url))
        if url:
            self.mw.show_toast("webhook saved", "success")
        else:
            self.mw.show_toast("webhook cleared", "info")

    def _test(self):
        url = self.wh.text().strip()
        if not url:
            self.mw.show_toast("enter a webhook url first", "warning")
            return
        from core.webhook import WebhookSender
        wh = WebhookSender(url)
        from core.scanner import ScanResult
        results = {"test": ScanResult()}
        ok, msg = wh.send_scan_report(results)
        if ok:
            self.mw.show_toast("webhook test sent", "success", 5000)
        else:
            self.mw.show_toast(f"webhook test failed: {msg}", "error", 6000)
