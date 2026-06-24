import os
import sys
import subprocess
import json
import shutil
import tempfile
import sqlite3
import urllib.request
import urllib.error
import zipfile
import ctypes
import struct
import re
import hashlib
from datetime import datetime
from pathlib import Path
from pathlib import Path


APPDATA = os.environ.get("APPDATA", "")
LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")
TEMP = os.environ.get("TEMP", "")
USERPROFILE = os.environ.get("USERPROFILE", "")
MINECRAFT = os.path.join(APPDATA, ".minecraft")
PROGRAMDATA = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
DOWNLOADS = os.path.join(LOCALAPPDATA, "ChichoSSHelper")

CHEAT_CLIENTS = [
    "Wurst", "Impact", "Meteor", "Aristois", "Liquidbounce", "Sigma",
    "Ares", "Future", "Vape", "Astolfo", "Drip", "Salhack", "Entropy",
    "Inertia", "Raven", "Novoline", "Wolfram", "PyroHax", "Rekt",
    "Remix", "XRay", "Horion", "Phi", "Hybrid", "Rusher", "cyemer",
    "Prestige", "velaris", "bleach", "vapor", "dusk", "azura", "vertex",
    "nexus", "rise", "lucid", "ketamine", "reflex", "exodus", "zenith"
]

SUSPICIOUS_PROCS = [
    "cheat", "hack", "inject", "ghost", "vape", "sigma",
    "future", "meteor", "wurst", "aristois", "payload", "rat",
    "keylog", "prestige", "bleach", "vapor", "dusk"
]

SUSPICIOUS_INJECTION_MODULES = [
    "inject", "hook", "cheat", "vape", "sigma",
    "future", "meteor", "wurst", "aristois", "payload"
]


class ScanResult:
    def __init__(self):
        self.found = []
        self.warnings = []
        self.info = []
        self.errors = []
        self.data = {}

    def add_found(self, msg, path=None):
        self.found.append((msg, path))

    def add_warning(self, msg, path=None):
        self.warnings.append((msg, path))

    def add_info(self, msg):
        self.info.append(msg)

    def add_error(self, msg):
        self.errors.append(msg)

    @property
    def has_issues(self):
        return len(self.found) > 0 or len(self.warnings) > 0

    @property
    def summary(self):
        parts = []
        if self.found:
            parts.append(f"{len(self.found)} found")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warnings")
        if self.errors:
            parts.append(f"{len(self.errors)} errors")
        return ", ".join(parts) if parts else "All clear"


class Scanner:
    def __init__(self):
        self.webhook_url = ""

    def set_webhook(self, url):
        self.webhook_url = url

    # ── Helpers ─────────────────────────────────────────────────────────

    def _run(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return ""

    def _is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    # ── AppData Scan ────────────────────────────────────────────────────

    def scan_appdata(self):
        result = ScanResult()
        for client in CHEAT_CLIENTS:
            for base in [APPDATA, LOCALAPPDATA]:
                path = os.path.join(base, client)
                if os.path.exists(path):
                    result.add_found(f"{client}", path)

        CHEAT_JAR_KEYWORDS = ["wurst", "sigma", "vape", "meteor", "aristois", "impact",
                               "liquidbounce", "prestige", "bleach", "vapor", "salhack",
                               "inertia", "raven", "novoline", "ares", "astolfo"]
        jar_out = self._run(f'dir "{APPDATA}" /s /b *.jar 2>nul')
        jar_lines = [l.strip() for l in jar_out.splitlines() if l.strip()]
        for line in jar_lines:
            if not line.lower().endswith(".jar"):
                continue
            if ".minecraft" not in line.lower():
                fname = os.path.basename(line).lower().replace("-", "").replace("_", "")
                if any(k in fname for k in CHEAT_JAR_KEYWORDS):
                    result.add_warning(f"Suspicious JAR", line)

        CHEAT_DLL_KEYWORDS = ["wurst", "sigma", "vape", "meteor", "prestige", "bleach", "vapor"]
        dll_out = self._run(f'dir "{APPDATA}" /s /b *.dll 2>nul')
        dll_lines = [l.strip() for l in dll_out.splitlines() if l.strip()]
        for line in dll_lines:
            if not line.lower().endswith(".dll"):
                continue
            fname = os.path.basename(line).lower().replace("-", "").replace("_", "")
            if any(k in fname for k in CHEAT_DLL_KEYWORDS):
                result.add_warning(f"Suspicious DLL", line)

        if not result.has_issues:
            result.add_info("No known cheat client folders found.")
        return result

    # ── Process Scan ────────────────────────────────────────────────────

    def scan_processes(self):
        result = ScanResult()
        all_procs = self._run("tasklist").lower()
        for s in SUSPICIOUS_PROCS:
            if s in all_procs:
                result.add_found(f"Process matching: {s}")

        java_info = self._run("tasklist /fi \"imagename eq javaw.exe\" /v")
        if java_info:
            result.add_info("Java processes found")
            result.data["java_output"] = java_info

        result.data["full_tasklist"] = self._run("tasklist /v")
        if not result.has_issues:
            result.add_info("No suspicious processes detected.")
        return result

    def scan_injection(self):
        result = ScanResult()
        for proc in ["javaw.exe", "java.exe"]:
            out = self._run(f'tasklist /m /fi "imagename eq {proc}"')
            if not out:
                continue
            for line in out.splitlines():
                text = line.lower()
                if proc in text and any(k in text for k in SUSPICIOUS_INJECTION_MODULES):
                    result.add_found(f"Injected module in {proc}", line.strip())
        if not result.has_issues:
            result.add_info("No suspicious injected modules found.")
        return result

    # ── Minecraft Scan ──────────────────────────────────────────────────

    def scan_minecraft(self):
        result = ScanResult()
        if not os.path.exists(MINECRAFT):
            result.add_warning(".minecraft folder not found")
            return result

        for folder in ["mods", "versions", "config", "resourcepacks", "shaderpacks"]:
            path = os.path.join(MINECRAFT, folder)
            if os.path.exists(path):
                files = os.listdir(path)
                result.data[f"{folder}_files"] = files
                result.add_info(f"{folder}: {len(files)} files")
            else:
                result.add_info(f"{folder}: not found")

        lp = os.path.join(MINECRAFT, "launcher_profiles.json")
        if os.path.exists(lp):
            try:
                with open(lp, "r", errors="ignore") as f:
                    data = json.load(f)
                profiles = data.get("profiles", {})
                for k, v in profiles.items():
                    jpath = v.get("javaDir", "default Java")
                    name = v.get("name", k)
                    if jpath and "program files" not in jpath.lower() and jpath != "default Java":
                        result.add_warning(f"Non-standard Java in profile '{name}'", jpath)
            except Exception as e:
                result.add_error(f"Could not parse launcher_profiles: {e}")

        log = os.path.join(MINECRAFT, "logs", "latest.log")
        if os.path.exists(log):
            with open(log, "r", errors="ignore") as f:
                for line in f:
                    if any(k in line.lower() for k in ["cheat", "inject", "wurst", "sigma", "vape", "hacked"]):
                        result.add_warning(f"Suspicious log entry", line.strip()[:200])
        else:
            result.add_info("No latest.log found.")

        return result

    # ── Java Arguments Scan ─────────────────────────────────────────────

    def scan_java_arguments(self):
        result = ScanResult()
        cmd = 'wmic process where "name=\'javaw.exe\' or name=\'java.exe\'" get ProcessId,CommandLine /format:list'
        out = self._run(cmd)
        if not out:
            result.add_info("No java processes found.")
            return result

        suspicious = ["-javaagent", "inject", "mixin", "tweakclass", "forge", "fabric", "plugin", "agent"]
        for line in out.splitlines():
            text = line.strip()
            if not text:
                continue
            if any(k in text.lower() for k in suspicious):
                result.add_warning("Suspicious java arg", text)
        return result

    # ── Suspicious Folders ──────────────────────────────────────────────

    def scan_suspicious_folders(self):
        result = ScanResult()
        bases = [
            APPDATA, LOCALAPPDATA,
            os.path.join(USERPROFILE, "Downloads"),
            os.path.join(USERPROFILE, "Desktop"),
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
            os.path.join(USERPROFILE, ".minecraft"),
        ]
        extra_names = ["badlion", "impact", "salhack", "liquidbounce", "disabler",
                       "meteor", "exploit", "payload", "bleach", "vapor", "dusk",
                       "azura", "vertex", "nexus", "rise", "lucid"]
        all_names = sorted(set(CHEAT_CLIENTS + extra_names), key=str.lower)

        for base in bases:
            if not base or not os.path.exists(base):
                continue
            for name in all_names:
                path = os.path.join(base, name)
                if os.path.exists(path):
                    result.add_found(f"{name}", path)

        if not result.has_issues:
            result.add_info("No suspicious folders found.")
        return result

    # ── Launcher Scan ───────────────────────────────────────────────────

    def _launcher_paths(self, name):
        candidates = []
        if name == "norisk":
            candidates = [
                os.path.join(LOCALAPPDATA, "norisk"),
                os.path.join(APPDATA, "norisk"),
            ]
        elif name == "prism":
            candidates = [
                os.path.join(APPDATA, "PrismLauncher"),
                os.path.join(APPDATA, "prismlauncher"),
                os.path.join(APPDATA, "prism-launcher"),
                os.path.join(APPDATA, "Prism Launcher"),
                os.path.join(LOCALAPPDATA, "Programs", "Prism Launcher"),
                os.path.join(LOCALAPPDATA, "PrismLauncher"),
            ]
        elif name == "lunar":
            candidates = [
                os.path.join(USERPROFILE, ".lunarclient", "offline", "multiver", "mods"),
                os.path.join(USERPROFILE, ".lunarclient", "offline"),
                os.path.join(USERPROFILE, ".lunarclient", "profiles"),
                os.path.join(USERPROFILE, ".lunarclient"),
                os.path.join(APPDATA, "LunarClient"),
                os.path.join(LOCALAPPDATA, "Programs", "Lunar Client"),
            ]
        elif name == "feather":
            candidates = [
                os.path.join(APPDATA, "feather"),
                os.path.join(APPDATA, "FeatherClient"),
                os.path.join(LOCALAPPDATA, "Programs", "Feather"),
            ]
        elif name == "modrinth":
            candidates = [
                os.path.join(APPDATA, "ModrinthApp", "profiles"),
                os.path.join(APPDATA, "ModrinthApp"),
                os.path.join(APPDATA, "com.modrinth.theseus", "profiles"),
                os.path.join(LOCALAPPDATA, "ModrinthApp", "profiles"),
                os.path.join(LOCALAPPDATA, "ModrinthApp"),
                os.path.join(LOCALAPPDATA, "com.modrinth.theseus"),
                os.path.join(LOCALAPPDATA, "Programs", "Modrinth App"),
            ]
        elif name == "curseforge":
            candidates = [
                os.path.join(USERPROFILE, "curseforge", "minecraft", "Instances"),
                os.path.join(APPDATA, "CurseForge"),
                os.path.join(LOCALAPPDATA, "CurseForge"),
                os.path.join(APPDATA, "Overwolf", "CurseForge"),
            ]
        elif name == "badlion":
            candidates = [
                os.path.join(APPDATA, "badlion client"),
                os.path.join(APPDATA, "Badlion Client"),
                os.path.join(LOCALAPPDATA, "Programs", "Badlion Client"),
            ]
        elif name == "tlauncher":
            candidates = [
                os.path.join(APPDATA, ".tlauncher"),
                os.path.join(APPDATA, "TLauncher"),
            ]
        elif name == "multimc":
            candidates = [
                os.path.join(APPDATA, "MultiMC"),
                os.path.join(LOCALAPPDATA, "Programs", "MultiMC"),
            ]
        elif name == ".minecraft":
            candidates = [os.path.join(MINECRAFT, "mods")]
        return [p for p in candidates if os.path.exists(p)]

    def scan_launchers(self):
        result = ScanResult()
        launchers = ["norisk", "prism", "lunar", "feather", "modrinth",
                     "curseforge", "badlion", "tlauncher", "multimc", ".minecraft"]
        for launcher in launchers:
            paths = self._launcher_paths(launcher)
            if not paths:
                result.add_info(f"{launcher}: not found")
                continue
            for path in paths:
                result.add_found(f"{launcher}", path)
                if os.path.isdir(path):
                    total = sum(len(files) for _, _, files in os.walk(path))
                    result.data[f"{launcher}_files"] = total
        return result

    def scan_launcher_mods(self, launcher, custom_path=None):
        result = ScanResult()
        if custom_path and os.path.exists(custom_path):
            paths = [custom_path]
        else:
            paths = self._launcher_paths(launcher)

        if not paths:
            result.add_warning(f"No path found for {launcher}")
            return result

        path = paths[0]
        matches = []
        for root, _, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith((".jar", ".zip", ".json")):
                    matches.append(os.path.relpath(os.path.join(root, filename), path))
                    if len(matches) >= 250:
                        break
            if len(matches) >= 250:
                break

        result.data["mods"] = matches
        result.data["launcher_path"] = path
        result.add_info(f"Found {len(matches)} mod/metadata files")
        return result

    # ── System Scans ────────────────────────────────────────────────────

    def scan_startup(self):
        result = ScanResult()
        result.data["hkcu_run"] = self._run("reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
        result.data["hklm_run"] = self._run("reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run")
        startup_folder = os.path.join(APPDATA, r"Microsoft\Windows\Start Menu\Programs\Startup")
        if os.path.exists(startup_folder):
            result.data["startup_files"] = os.listdir(startup_folder)
        return result

    def scan_temp(self):
        result = ScanResult()
        for ext in ["*.exe", "*.jar", "*.dll", "*.bat", "*.ps1"]:
            out = self._run(f'dir "{TEMP}" /b {ext} 2>nul')
            for line in out.splitlines():
                if line.strip():
                    result.add_warning(f"{ext} file in TEMP", os.path.join(TEMP, line.strip()))
        return result

    def scan_prefetch(self):
        result = ScanResult()
        keywords = ["java", "cheat", "inject", "hack", "wurst", "sigma", "vape", "rat",
                    "bleach", "vapor", "dusk", "ccleaner", "bleachbit", "prestige"]
        out = self._run("dir C:\\Windows\\Prefetch /od /b *.pf 2>nul")
        for line in out.splitlines():
            if any(k in line.lower() for k in keywords):
                result.add_found(f"Prefetch: {line.strip()}")
        return result

    def scan_network(self):
        result = ScanResult()
        result.data["netstat"] = self._run("netstat -ano")
        return result

    def scan_hosts(self):
        result = ScanResult()
        hosts = r"C:\Windows\System32\drivers\etc\hosts"
        if os.path.exists(hosts):
            with open(hosts, "r") as f:
                result.data["hosts_content"] = f.read()
        return result

    def scan_programs(self):
        result = ScanResult()
        out = self._run('reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall /s /v DisplayName')
        programs = []
        for line in out.splitlines():
            if "DisplayName" in line:
                name = line.split("DisplayName")[-1].strip().lstrip("REG_SZ").strip()
                if name:
                    programs.append(name)
        result.data["programs"] = programs
        return result

    def scan_tasks(self):
        result = ScanResult()
        result.data["tasks"] = self._run("schtasks /query /fo LIST")
        return result

    def scan_vpn(self):
        result = ScanResult()
        out = self._run("ipconfig /all")
        for line in out.splitlines():
            if "description" in line.lower():
                if any(k in line.lower() for k in ["virtual", "vpn", "tap", "tunnel", "hyper-v", "hamachi"]):
                    result.add_found("VPN/Virtual adapter", line.strip())
        return result

    def scan_modified_files(self):
        result = ScanResult()
        desktop = self._run(f'forfiles /p "{USERPROFILE}\\Desktop" /s /d 0 /c "cmd /c echo @path" 2>nul')
        if desktop:
            result.data["desktop_modified"] = desktop.splitlines()
        appdata_files = self._run(f'forfiles /p "{APPDATA}" /s /d 0 /c "cmd /c echo @path" 2>nul')
        if appdata_files:
            result.data["appdata_modified"] = appdata_files.splitlines()
        return result

    def scan_drivers(self):
        result = ScanResult()
        result.data["drivers"] = self._run("driverquery")
        return result

    def scan_recent_files(self):
        result = ScanResult()
        path = os.path.join(APPDATA, r"Microsoft\Windows\Recent")
        if os.path.exists(path):
            files = sorted(
                [f for f in os.listdir(path)],
                key=lambda f: os.path.getmtime(os.path.join(path, f)),
                reverse=True
            )
            result.data["recent_files"] = files[:40]
        return result

    def scan_shadow_copies(self):
        result = ScanResult()
        result.data["vssadmin"] = self._run("vssadmin list shadows")
        result.data["wmic_shadow"] = self._run("wmic shadowcopy list brief")
        return result

    # ── Report Generation ──────────────────────────────────────────────

    def generate_report(self, results):
        user = os.environ.get("USERNAME", "unknown")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = []
        lines.append("=" * 60)
        lines.append("  sechan-ss scan report")
        lines.append("=" * 60)
        lines.append(f"  user:     {user}")
        lines.append(f"  date:     {now}")
        lines.append(f"  host:     {os.environ.get('COMPUTERNAME', 'unknown')}")
        lines.append(f"  os:       {os.environ.get('OS', 'unknown')}")
        lines.append("=" * 60)
        lines.append("")

        total_issues = 0
        total_warns = 0

        for name, result in results.items():
            lines.append(f"--- {name} ---")
            if result.found:
                total_issues += len(result.found)
                for msg, path in result.found:
                    p = f"  ->  {path}" if path else ""
                    lines.append(f"  [!!] {msg}{p}")
            if result.warnings:
                total_warns += len(result.warnings)
                for msg, path in result.warnings:
                    p = f"  ->  {path}" if path else ""
                    lines.append(f"  [!]  {msg}{p}")
            if result.info:
                for msg in result.info:
                    lines.append(f"  [~]  {msg}")
            if not result.found and not result.warnings and not result.info:
                lines.append(f"  [ok]  clean")
            lines.append("")

        lines.append("=" * 60)
        lines.append(f"  summary: {total_issues} issues, {total_warns} warnings")
        lines.append("=" * 60)
        return "\n".join(lines)

    def save_report(self, results):
        user = os.environ.get("USERNAME", "unknown")
        now = datetime.now()
        report_dir = Path(os.environ.get("USERPROFILE", "C:\\")) / "Documents" / "sechan-ss" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        filename = f"scan_{user}_{now.strftime('%Y-%m-%d_%H%M%S')}.txt"
        filepath = report_dir / filename
        report = self.generate_report(results)
        filepath.write_text(report, encoding="utf-8")
        return str(filepath)

    def send_webhook(self, results):
        if not self.webhook_url:
            return False, "no webhook configured"
        from .webhook import WebhookSender
        wh = WebhookSender(self.webhook_url)
        return wh.send_scan_report(results)

    # ── Full Scan ───────────────────────────────────────────────────────

    def full_scan(self, callback=None):
        results = {}
        scans = [
            ("AppData", self.scan_appdata),
            ("Processes", self.scan_processes),
            ("Injection", self.scan_injection),
            ("Minecraft", self.scan_minecraft),
            ("Java Args", self.scan_java_arguments),
            ("Suspicious Folders", self.scan_suspicious_folders),
            ("Launchers", self.scan_launchers),
            ("Startup", self.scan_startup),
            ("Temp", self.scan_temp),
            ("Prefetch", self.scan_prefetch),
        ]
        total = len(scans)
        for i, (name, scan_func) in enumerate(scans):
            if callback:
                callback(name, i + 1, total)
            try:
                results[name] = scan_func()
            except Exception as e:
                r = ScanResult()
                r.add_error(str(e))
                results[name] = r
        return results
