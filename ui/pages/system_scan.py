from PySide6.QtCore import QThread, Signal
from core.scanner import Scanner
from .base_page import BasePage


class Worker(QThread):
    done = Signal(dict)
    err = Signal(str)

    def run(self):
        try:
            s = Scanner()
            r = {
                "startup": s.scan_startup(),
                "temp": s.scan_temp(),
                "prefetch": s.scan_prefetch(),
                "network": s.scan_network(),
                "vpn": s.scan_vpn(),
                "programs": s.scan_programs(),
                "tasks": s.scan_tasks(),
                "hosts": s.scan_hosts(),
                "drivers": s.scan_drivers(),
                "recent": s.scan_recent_files(),
            }
            self.done.emit(r)
        except Exception as e:
            self.err.emit(str(e))


class SystemScanPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self._build("system scan", "startup / temp / prefetch / vpn / etc", self._go)

    def _go(self):
        self._busy(True)
        self.output.clear_output()
        self.output.append_info("scanning system...")
        self.w = Worker()
        self.w.done.connect(self._done)
        self.w.err.connect(self._err)
        self.w.start()

    def _done(self, results):
        self._busy(False)
        self.output.append_success("-- system scan --\n")
        issues = 0

        for name, r in results.items():
            self.output.append(f"\n<b>== {name.upper()} ==</b>")
            if r.found:
                issues += len(r.found)
                for m, p in r.found:
                    self.output.append_found(f"{m}  ->  {p}")
            if r.warnings:
                for m, p in r.warnings:
                    self.output.append_warning(f"{m}: {p}")
            if r.info:
                for m in r.info:
                    self.output.append_info(m)
            if r.data:
                for k, v in r.data.items():
                    if isinstance(v, list) and len(v) < 25:
                        for item in v[:15]:
                            self.output.append(f"  {item}")
                    elif isinstance(v, str) and len(v) < 1500 and v.strip():
                        for line in v.splitlines()[:12]:
                            self.output.append(f"  {line}")

        if issues:
            self.mw.show_toast(f"{issues} issues found", "warning", 5000)
        else:
            self.mw.show_toast("clean", "success")

    def _err(self, msg):
        self._busy(False)
        self.output.append_found(f"error: {msg}")
