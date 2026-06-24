from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
import os, subprocess

from .base_page import BasePage
from ..widgets import Card, StatCard
from ..theme import Colors
from core.scanner import Scanner
from core.tempserver import TempFileServer


class FullScanWorker(QThread):
    progress = Signal(str, int, int)
    finished = Signal(dict, str, str)
    webhook_result = Signal(bool, str)
    error = Signal(str)

    def __init__(self, webhook_url=""):
        super().__init__()
        self.webhook_url = webhook_url

    def run(self):
        try:
            s = Scanner()
            if self.webhook_url:
                s.set_webhook(self.webhook_url)
            results = s.full_scan(callback=self._p)
            report_path = s.save_report(results)

            dl_url = ""
            temp_server = TempFileServer()
            dl_url = temp_server.start(report_path, lifetime=900)

            wh_ok = None
            wh_msg = None
            if self.webhook_url:
                from core.webhook import WebhookSender
                wh = WebhookSender(self.webhook_url)
                wh_ok, wh_msg = wh.send_scan_report(results, dl_url)

            self.finished.emit(results, report_path, dl_url)
            if wh_ok is not None:
                self.webhook_result.emit(wh_ok, wh_msg)
        except Exception as e:
            self.error.emit(str(e))

    def _p(self, n, c, t):
        self.progress.emit(n, c, t)


class DashboardPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.scanner = Scanner()
        self.last_report_path = None
        self.last_dl_url = ""
        self._pv = 0

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
        t = QLabel("$ dashboard")
        t.setStyleSheet("color: #d4d4d4; font-size: 14px; font-weight: bold; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        hl.addWidget(t)
        hl.addStretch()
        s = QLabel("full system scan")
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

        stats = QHBoxLayout()
        stats.setSpacing(6)
        self.s_issues = StatCard("issues", "0", Colors.ACCENT_DANGER)
        self.s_warns = StatCard("warnings", "0", Colors.ACCENT_WARNING)
        self.s_clean = StatCard("clean", "0", Colors.ACCENT_SUCCESS)
        self.s_scans = StatCard("scans", "0", Colors.ACCENT_PRIMARY)
        stats.addWidget(self.s_issues)
        stats.addWidget(self.s_warns)
        stats.addWidget(self.s_clean)
        stats.addWidget(self.s_scans)
        cl.addLayout(stats)

        ac = Card()
        t2 = QLabel("# actions")
        t2.setObjectName("cardTitle")
        ac.layout().addWidget(t2)

        br = QHBoxLayout()
        br.setSpacing(6)
        self.run_btn = QPushButton("run full scan")
        self.run_btn.setObjectName("primaryButton")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self._run)
        self.run_btn.setMinimumHeight(32)
        self.clr_btn = QPushButton("clear")
        self.clr_btn.setObjectName("dangerButton")
        self.clr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clr_btn.clicked.connect(self._clear)
        self.clr_btn.setMinimumHeight(32)
        br.addWidget(self.run_btn)
        br.addWidget(self.clr_btn)
        br.addStretch()
        ac.layout().addLayout(br)

        self.p_label = QLabel("ready")
        self.p_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        ac.layout().addWidget(self.p_label)

        self.pbar = QFrame()
        self.pbar.setFixedHeight(14)
        self.pbar.setVisible(False)
        self.pbar.setStyleSheet(f"background-color: {Colors.BG_MEDIUM}; border: 1px solid {Colors.BORDER};")
        self.pfill = QFrame(self.pbar)
        self.pfill.setFixedHeight(14)
        self.pfill.setStyleSheet("background-color: #094771;")
        self.pfill.setFixedWidth(0)
        ac.layout().addWidget(self.pbar)
        cl.addWidget(ac)

        rc = Card()
        t3 = QLabel("# results")
        t3.setObjectName("cardTitle")
        rc.layout().addWidget(t3)

        self.ra = QLabel("no results yet. run a scan.")
        self.ra.setWordWrap(True)
        self.ra.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: 12px;
            padding: 10px;
            background-color: {Colors.BG_INPUT};
            border: 1px solid {Colors.BORDER};
            font-family: 'Cascadia Code', 'Consolas', monospace;
        """)
        self.ra.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.ra.setMinimumHeight(100)
        rc.layout().addWidget(self.ra)

        self.open_btn = QPushButton("open report file")
        self.open_btn.setVisible(False)
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn.setMinimumHeight(30)
        self.open_btn.clicked.connect(self._open_report)
        rc.layout().addWidget(self.open_btn)

        cl.addWidget(rc)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    def _run(self):
        self.run_btn.setEnabled(False)
        self.run_btn.setText("scanning...")
        self.ra.setText("scanning...")
        self.open_btn.setVisible(False)
        self.p_label.setVisible(True)
        self.p_label.setText("starting...")
        self.pbar.setVisible(True)
        self._pv = 0
        self.pfill.setFixedWidth(0)

        webhook_url = getattr(self.mw, 'webhook_url', '')

        self.worker = FullScanWorker(webhook_url)
        self.worker.progress.connect(self._on_p)
        self.worker.finished.connect(self._on_done)
        self.worker.webhook_result.connect(self._on_wh)
        self.worker.error.connect(self._on_err)
        self.worker.start()

    def _on_p(self, name, cur, total):
        self.p_label.setText(f"[{cur}/{total}] {name}")
        w = int((cur / total) * self.pbar.width())
        self.pfill.setFixedWidth(max(w, 4))

    def _on_done(self, results, report_path, dl_url=""):
        self.last_report_path = report_path
        self.last_dl_url = dl_url
        self.run_btn.setEnabled(True)
        self.run_btn.setText("run full scan")
        self.p_label.setText("done")
        QTimer.singleShot(3000, lambda: self.p_label.setText("ready"))
        QTimer.singleShot(3000, lambda: self.pbar.setVisible(False))
        self.pfill.setFixedWidth(self.pbar.width())

        issues = sum(len(r.found) for r in results.values())
        warns = sum(len(r.warnings) for r in results.values())
        total = len(results)

        self.s_issues.set_value(str(issues))
        self.s_warns.set_value(str(warns))
        self.s_clean.set_value(str(max(total - (1 if issues else 0) - (1 if warns else 0), 0)))
        self.s_scans.set_value(str(total))

        short = []
        for name, r in results.items():
            if r.found:
                short.append(f"  {name}: {len(r.found)} found")
            if r.warnings:
                short.append(f"  {name}: {len(r.warnings)} warnings")
        summary = "\n".join(short) if short else "  all clean"

        dl_text = f"\ndownload link (15m):\n  {dl_url}" if dl_url else ""
        self.ra.setText(
            f"scan complete\n"
            f"  {issues} issues, {warns} warnings across {total} checks\n"
            f"\n{summary}\n"
            f"\nreport saved to:\n  {report_path}"
            f"{dl_text}"
        )
        self.open_btn.setVisible(True)

        if issues:
            self.mw.show_toast(f"{issues} issues, {warns} warnings", "warning", 5000)
        else:
            self.mw.show_toast("all clear", "success", 4000)

    def _on_wh(self, ok, msg):
        if ok:
            self.mw.show_toast("webhook sent", "success", 3000)
        else:
            self.mw.show_toast(f"webhook: {msg}", "warning", 4000)

    def _on_err(self, msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("run full scan")
        self.p_label.setText("failed")
        self.ra.setText(f"error: {msg}")
        self.mw.show_toast(f"error: {msg}", "error", 5000)

    def _open_report(self):
        if self.last_report_path and os.path.exists(self.last_report_path):
            subprocess.Popen(["notepad.exe", self.last_report_path])

    def _clear(self):
        self.ra.setText("no results yet. run a scan.")
        self.s_issues.set_value("0")
        self.s_warns.set_value("0")
        self.s_clean.set_value("0")
        self.s_scans.set_value("0")
        self.p_label.setText("ready")
        self.pbar.setVisible(False)
        self.open_btn.setVisible(False)
        self.last_report_path = None
        self.last_dl_url = ""

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'pbar') and self.pbar.isVisible():
            w = int((self._pv / 100) * self.pbar.width())
            self.pfill.setFixedWidth(max(w, 4))
