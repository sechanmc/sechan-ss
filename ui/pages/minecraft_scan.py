from PySide6.QtCore import QThread, Signal
from core.scanner import Scanner
from .base_page import BasePage


class Worker(QThread):
    done = Signal(object)
    err = Signal(str)

    def run(self):
        try:
            s = Scanner()
            self.done.emit((s.scan_minecraft(), s.scan_suspicious_folders()))
        except Exception as e:
            self.err.emit(str(e))


class MinecraftScanPage(BasePage):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self._build("minecraft scan", ".minecraft / mods / cheat folders", self._go)

    def _go(self):
        self._busy(True)
        self.output.clear_output()
        self.output.append_info("scanning minecraft...")
        self.w = Worker()
        self.w.done.connect(self._done)
        self.w.err.connect(self._err)
        self.w.start()

    def _done(self, r):
        self._busy(False)
        mc, folders = r
        self.output.append_success("-- minecraft scan --\n")

        self.output.append_info("-- .minecraft structure --")
        for k in ["mods_files", "versions_files", "config_files", "resourcepacks_files", "shaderpacks_files"]:
            if k in mc.data:
                label = k.replace("_files", "")
                files = mc.data[k]
                self.output.append_info(f"{label}: {len(files)} files")
                for f in files[:15]:
                    self.output.append(f"  {f}")

        if mc.warnings:
            self.output.append_divider()
            self.output.append_info("-- warnings --")
            for m, p in mc.warnings:
                self.output.append_warning(f"{m}: {p}")

        self.output.append_divider()
        self.output.append_info("-- cheat folders --")
        if folders.found:
            for m, p in folders.found:
                self.output.append_found(f"{m}  ->  {p}")
        else:
            self.output.append_info("none found")

        if mc.has_issues or folders.has_issues:
            self.mw.show_toast("suspicious items found", "warning", 5000)
        else:
            self.mw.show_toast("clean", "success")

    def _err(self, msg):
        self._busy(False)
        self.output.append_found(f"error: {msg}")
