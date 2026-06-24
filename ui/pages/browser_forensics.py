from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor

from .base_page import BasePage
from ..widgets import Card
from ..theme import Colors
from core.forensics import BrowserForensics


class Worker(QThread):
    done = Signal(object, str)
    err = Signal(str)

    def __init__(self, st):
        super().__init__()
        self.st = st

    def run(self):
        try:
            f = BrowserForensics()
            types = {
                "history": f.check_history, "downloads": f.check_downloads,
                "wipe": f.check_wipe_detection, "cookies": f.check_cookies,
                "cheat": f.check_cheat_sites,
            }
            self.done.emit(types[self.st](), self.st)
        except Exception as e:
            self.err.emit(str(e))


SCANS = [("history", "history"), ("downloads", "downloads"), ("wipe", "wipe"),
         ("cookies", "cookies"), ("cheat", "cheat sites")]


class BrowserForensicsPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw

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
        t = QLabel("$ browser forensics")
        t.setStyleSheet("color: #d4d4d4; font-size: 14px; font-weight: bold; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        hl.addWidget(t)
        hl.addStretch()
        s = QLabel("history / downloads / cookies / cheat sites")
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

        ac = Card()
        t2 = QLabel("# scans")
        t2.setObjectName("cardTitle")
        ac.layout().addWidget(t2)

        br = QHBoxLayout()
        br.setSpacing(6)
        self.btns = {}
        for st, lb in SCANS:
            b = QPushButton(lb)
            b.setObjectName("forensicButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setMinimumHeight(30)
            b.clicked.connect(lambda checked, s=st: self._run(s))
            br.addWidget(b)
            self.btns[st] = b
        ac.layout().addLayout(br)

        self.sl = QLabel("select a scan")
        self.sl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; background: transparent; font-family: 'Cascadia Code', 'Consolas', monospace;")
        ac.layout().addWidget(self.sl)
        cl.addWidget(ac)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["time", "browser", "type", "details", "status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(200)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        cl.addWidget(self.table, 1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    def _run(self, st):
        self.table.setRowCount(0)
        self.sl.setText(f"scanning {st}...")
        for b in self.btns.values():
            b.setEnabled(b != self.btns[st] or False)
        self.btns[st].setEnabled(False)
        self.w = Worker(st)
        self.w.done.connect(self._done)
        self.w.err.connect(self._err)
        self.w.start()

    def _done(self, r, st):
        for b in self.btns.values():
            b.setEnabled(True)
        self.table.setRowCount(0)

        for w in r.warnings:
            row = self.table.rowCount()
            self.table.insertRow(row)
            wi = QTableWidgetItem("!")
            wi.setForeground(QColor(Colors.ACCENT_WARNING))
            self.table.setItem(row, 0, wi)
            self.table.setItem(row, 1, QTableWidgetItem(""))
            self.table.setItem(row, 2, QTableWidgetItem("WARN"))
            self.table.setItem(row, 3, QTableWidgetItem(w))
            self.table.setItem(row, 4, QTableWidgetItem(""))

        if not r.entries and not r.warnings:
            for m in r.info:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(""))
                self.table.setItem(row, 1, QTableWidgetItem(""))
                self.table.setItem(row, 2, QTableWidgetItem("INFO"))
                self.table.setItem(row, 3, QTableWidgetItem(m))
                self.table.setItem(row, 4, QTableWidgetItem(""))

        for e in r.entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(e["timestamp"]))
            self.table.setItem(row, 1, QTableWidgetItem(e["browser"]))
            ti = QTableWidgetItem(e["type"])
            if e["suspicious"]:
                ti.setForeground(QColor(Colors.ACCENT_DANGER))
            self.table.setItem(row, 2, ti)
            details = e["url"]
            if e["title"]:
                details = f"{e['title'][:60]} - {e['url'][:80]}"
            self.table.setItem(row, 3, QTableWidgetItem(details))
            if e["suspicious"]:
                badge = QTableWidgetItem("SUSPICIOUS")
                badge.setForeground(QColor(Colors.ACCENT_DANGER))
                badge.setBackground(QColor("#3a1a1a"))
                self.table.setItem(row, 4, badge)
            else:
                self.table.setItem(row, 4, QTableWidgetItem(""))
            self.table.setRowHeight(row, 28)

        labels = {"history": "history entries", "downloads": "downloads",
                   "wipe": "indicators", "cookies": "domains", "cheat": "matches"}
        sus = any(e["suspicious"] for e in r.entries)
        self.sl.setText(f"{len(r.entries)} {labels.get(st, 'results')}")
        self.mw.show_toast(f"{len(r.entries)} {labels.get(st, 'results')}",
                          "warning" if sus else "info", 4000)

    def _err(self, msg):
        for b in self.btns.values():
            b.setEnabled(True)
        self.table.setRowCount(0)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("ERROR"))
        self.table.setItem(row, 3, QTableWidgetItem(msg))
        self.sl.setText("failed")
