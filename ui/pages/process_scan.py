from PySide6.QtCore import QThread, Signal
from core.scanner import Scanner
from .base_page import BasePage


class Worker(QThread):
    done = Signal(object)
    err = Signal(str)

    def run(self):
        try:
            s = Scanner()
            self.done.emit((s.scan_processes(), s.scan_java_arguments()))
        except Exception as e:
            self.err.emit(str(e))


class ProcessScanPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self._build("process scan", "running tasks / java args", self._go)

    def _go(self):
        self._busy(True)
        self.output.clear_output()
        self.output.append_info("scanning processes...")
        self.w = Worker()
        self.w.done.connect(self._done)
        self.w.err.connect(self._err)
        self.w.start()

    def _done(self, r):
        self._busy(False)
        res, jargs = r
        self.output.append_success("-- process scan --\n")
        if res.found:
            for m, _ in res.found:
                self.output.append_found(m)
        else:
            self.output.append_info("no suspicious processes")

        self.output.append_divider()
        self.output.append_info("-- java args --")
        if jargs.warnings:
            for m, p in jargs.warnings:
                self.output.append_warning(f"{m}: {p}")
        else:
            self.output.append_info("no suspicious java args")

        if "full_tasklist" in res.data:
            self.output.append_divider()
            self.output.append_info("-- process list (first 30) --")
            for line in res.data["full_tasklist"].splitlines()[:30]:
                self.output.append(line)

        if res.has_issues or jargs.has_issues:
            self.mw.show_toast("suspicious processes", "warning", 5000)
        else:
            self.mw.show_toast("clean", "success")

    def _err(self, msg):
        self._busy(False)
        self.output.append_found(f"error: {msg}")
