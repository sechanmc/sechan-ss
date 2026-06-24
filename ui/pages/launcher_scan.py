from PySide6.QtWidgets import QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit
from PySide6.QtCore import Qt, QThread, Signal
from core.scanner import Scanner
from .base_page import BasePage
from ..theme import Colors


class Worker(QThread):
    done = Signal(object)
    err = Signal(str)

    def __init__(self, launcher, custom_path=None):
        super().__init__()
        self.launcher = launcher
        self.custom_path = custom_path

    def run(self):
        try:
            s = Scanner()
            r = s.scan_launcher_mods(self.launcher, self.custom_path)
            al = s.scan_launchers()
            self.done.emit((r, al))
        except Exception as e:
            self.err.emit(str(e))


LAUNCHERS = [
    ("norisk", "norisk"), ("prism", "prism"), ("lunar", "lunar"),
    ("feather", "feather"), ("modrinth", "modrinth"), ("curseforge", "curseforge"),
    ("badlion", "badlion"), ("tlauncher", "tlauncher"), ("multimc", "multimc"),
    (".minecraft", ".minecraft"),
]


class LauncherScanPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self._build("launcher scan", "mods / profiles / configs", self._go)

        # inject selector after status
        sr = QHBoxLayout()
        sr.setSpacing(6)
        lb = QLabel("launcher:")
        lb.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; background: transparent;")
        sr.addWidget(lb)

        self.combo = QComboBox()
        self.combo.setMinimumWidth(140)
        for label, val in LAUNCHERS:
            self.combo.addItem(label, val)
        sr.addWidget(self.combo)

        self.custom = QLineEdit()
        self.custom.setPlaceholderText("custom path...")
        sr.addWidget(self.custom, 1)

        idx = self.layout().indexOf(self.status)
        self.layout().insertLayout(idx, sr)

    def _go(self):
        launcher = self.combo.currentData()
        custom = self.custom.text().strip()
        self._busy(True)
        self.output.clear_output()
        self.output.append_info(f"scanning: {launcher}" + (f" ({custom})" if custom else ""))
        self.w = Worker(launcher, custom if custom else None)
        self.w.done.connect(self._done)
        self.w.err.connect(self._err)
        self.w.start()

    def _done(self, r):
        self._busy(False)
        mods, all_l = r
        self.output.append_success("-- launcher scan --\n")

        self.output.append_info("-- detected launchers --")
        if all_l.found:
            for m, p in all_l.found:
                self.output.append_found(f"{m}  ->  {p}")
        else:
            for m in all_l.info:
                self.output.append_info(m)

        if mods.data.get("launcher_path"):
            path = mods.data["launcher_path"]
            files = mods.data.get("mods", [])
            self.output.append_divider()
            self.output.append_info(f"-- files ({path}) --")
            if files:
                for f in files:
                    self.output.append(f"  {f}")
            else:
                self.output.append_info("no mod files found")

        if mods.warnings:
            for m, p in mods.warnings:
                self.output.append_warning(f"{m}: {p}")

        self.mw.show_toast("scan complete", "success")

    def _err(self, msg):
        self._busy(False)
        self.output.append_found(f"error: {msg}")
