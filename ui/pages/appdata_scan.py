from PySide6.QtCore import QThread, Signal
from core.scanner import Scanner
from .base_page import BasePage


class Worker(QThread):
    done = Signal(object)
    err = Signal(str)

    def run(self):
        try:
            s = Scanner()
            self.done.emit((s.scan_appdata(), s.scan_injection()))
        except Exception as e:
            self.err.emit(str(e))


class AppDataScanPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self._build("appdata scan", "cheat clients / suspicious dlls", self._go)

    def _go(self):
        self._busy(True)
        self.output.clear_output()
        self.output.append_info("scanning appdata...")
        self.w = Worker()
        self.w.done.connect(self._done)
        self.w.err.connect(self._err)
        self.w.start()

    def _done(self, r):
        self._busy(False)
        res, inj = r
        self.output.append_success("-- appdata scan --\n")
        if res.found:
            for m, p in res.found:
                self.output.append_found(f"{m}  ->  {p}")
        else:
            self.output.append_info("no known cheat clients")

        if res.warnings:
            self.output.append_divider()
            for m, p in res.warnings:
                self.output.append_warning(f"{m}: {p}")

        self.output.append_divider()
        self.output.append_info("-- injection check --")
        if inj.found:
            for m, p in inj.found:
                self.output.append_found(f"{m}: {p}")
        else:
            self.output.append_info("no injected modules")

        if res.has_issues or inj.has_issues:
            self.mw.show_toast("suspicious items found", "warning", 5000)
        else:
            self.mw.show_toast("clean", "success")

    def _err(self, msg):
        self._busy(False)
        self.output.append_found(f"error: {msg}")
