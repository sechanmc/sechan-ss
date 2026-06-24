import os
import sqlite3
import shutil
import tempfile
from datetime import datetime


LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")
APPDATA = os.environ.get("APPDATA", "")

BROWSER_PROFILES = {
    "Chrome":  os.path.join(LOCALAPPDATA, r"Google\Chrome\User Data"),
    "Edge":    os.path.join(LOCALAPPDATA, r"Microsoft\Edge\User Data"),
    "Brave":   os.path.join(LOCALAPPDATA, r"BraveSoftware\Brave-Browser\User Data"),
    "Opera":   os.path.join(APPDATA,      r"Opera Software\Opera Stable"),
    "Vivaldi": os.path.join(LOCALAPPDATA, r"Vivaldi\User Data"),
}

FIREFOX_ROOT = os.path.join(APPDATA, r"Mozilla\Firefox\Profiles")

CHEAT_SITE_KEYWORDS = [
    "cheat", "hack", "inject", "ghost", "crack", "nulled", "warez",
    "leaked", "bypass", "skid", "payload", "exploit", "trainer", "client",
    "prestige", "reflex", "exodus", "zenith", "ketamine",
    "Wurst", "Impact", "Meteor", "Aristois", "Liquidbounce", "Sigma",
    "Ares", "Future", "Vape", "Astolfo", "Drip", "Salhack", "Entropy",
    "Inertia", "Raven", "Novoline", "Wolfram", "PyroHax", "Rekt",
    "Remix", "XRay", "Horion", "Phi", "Hybrid", "Rusher", "cyemer",
    "Prestige", "velaris", "bleach", "vapor", "dusk", "azura", "vertex",
    "nexus", "rise", "lucid", "ketamine", "reflex", "exodus", "zenith",
    "blackspigot", "spigotunlocked", "mcleaks", "tlauncher", "cracked",
    "freemc", "freeminecraft", "altening", "thealtening", "easymc",
    "minecraftalt", "skyclient",
]

SAFE_DOMAINS = [
    "google.com", "youtube.com", "discord.com", "reddit.com", "microsoft.com",
    "minecraft.net", "mojang.com", "curseforge.com", "modrinth.com",
    "fabricmc.net", "minecraftforge.net", "optifine.net", "github.com",
    "twitch.tv", "wikipedia.org", "cloudflare.com", "gstatic.com",
    "googleapis.com", "badlion.net", "lunarclient.com",
]


class ForensicsResult:
    def __init__(self):
        self.entries = []
        self.warnings = []
        self.info = []

    def add_entry(self, browser, profile, entry_type, url, title, timestamp, is_suspicious=False):
        self.entries.append({
            "browser": browser,
            "profile": profile,
            "type": entry_type,
            "url": url,
            "title": title,
            "timestamp": timestamp,
            "suspicious": is_suspicious,
        })

    def add_warning(self, msg):
        self.warnings.append(msg)

    def add_info(self, msg):
        self.info.append(msg)


class BrowserForensics:
    def __init__(self):
        pass

    def _chromium_profiles(self, browser_root):
        profiles = []
        if not os.path.isdir(browser_root):
            return profiles
        for entry in os.listdir(browser_root):
            full = os.path.join(browser_root, entry)
            if os.path.isdir(full) and (entry == "Default" or entry.startswith("Profile")):
                profiles.append(full)
        return profiles

    def _copy_db(self, db_path):
        tmp = tempfile.mktemp(suffix=".db")
        shutil.copy2(db_path, tmp)
        return tmp

    def check_history(self):
        result = ForensicsResult()
        for browser, root in BROWSER_PROFILES.items():
            profiles = self._chromium_profiles(root)
            if not profiles:
                continue
            for profile in profiles:
                hist_db = os.path.join(profile, "History")
                if not os.path.exists(hist_db):
                    continue
                try:
                    tmp = self._copy_db(hist_db)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT url, title, visit_count,
                               datetime(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime')
                        FROM urls ORDER BY last_visit_time DESC LIMIT 50
                    """)
                    for url, title, visits, ts in cur.fetchall():
                        result.add_entry(
                            browser, os.path.basename(profile), "HISTORY",
                            url, title or "", ts
                        )
                    conn.close()
                    os.remove(tmp)
                except Exception as e:
                    result.add_warning(f"Could not read {browser} history: {e}")

        if os.path.isdir(FIREFOX_ROOT):
            for profile in os.listdir(FIREFOX_ROOT):
                places = os.path.join(FIREFOX_ROOT, profile, "places.sqlite")
                if not os.path.exists(places):
                    continue
                try:
                    tmp = self._copy_db(places)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT p.url, p.title,
                               datetime(h.visit_date/1000000, 'unixepoch', 'localtime')
                        FROM moz_places p
                        JOIN moz_historyvisits h ON h.place_id = p.id
                        ORDER BY h.visit_date DESC LIMIT 50
                    """)
                    for url, title, ts in cur.fetchall():
                        result.add_entry(
                            "Firefox", profile, "HISTORY",
                            url, title or "", ts
                        )
                    conn.close()
                    os.remove(tmp)
                except Exception as e:
                    result.add_warning(f"Could not read Firefox history: {e}")

        if not result.entries:
            result.add_info("No browser history found.")
        return result

    def check_downloads(self):
        result = ForensicsResult()
        for browser, root in BROWSER_PROFILES.items():
            profiles = self._chromium_profiles(root)
            if not profiles:
                continue
            for profile in profiles:
                hist_db = os.path.join(profile, "History")
                if not os.path.exists(hist_db):
                    continue
                try:
                    tmp = self._copy_db(hist_db)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT target_path, tab_url, total_bytes, received_bytes,
                               datetime(start_time/1000000-11644473600, 'unixepoch', 'localtime'),
                               state, danger_type
                        FROM downloads ORDER BY start_time DESC LIMIT 100
                    """)
                    for target, tab_url, total, received, ts, state, danger in cur.fetchall():
                        fname = os.path.basename(target or "?")
                        ext = os.path.splitext(fname)[1].lower()
                        suspicious = ext in [".jar", ".exe", ".dll", ".bat", ".ps1", ".vbs", ".zip"]
                        still_on = os.path.exists(target or "")
                        label = "DOWNLOAD" if still_on else "DOWNLOAD [DELETED]"
                        result.add_entry(
                            browser, os.path.basename(profile), label,
                            tab_url or target, fname, ts, suspicious
                        )
                    conn.close()
                    os.remove(tmp)
                except Exception as e:
                    result.add_warning(f"Could not read {browser} downloads: {e}")

        if not result.entries:
            result.add_info("No browser downloads found.")
        return result

    def check_wipe_detection(self):
        result = ForensicsResult()
        suspicious_found = False

        for browser, root in BROWSER_PROFILES.items():
            profiles = self._chromium_profiles(root)
            if not profiles:
                continue
            for profile in profiles:
                hist_db = os.path.join(profile, "History")
                pname = os.path.basename(profile)
                if not os.path.exists(hist_db):
                    result.add_warning(f"{browser} [{pname}]: History MISSING — likely wiped!")
                    suspicious_found = True
                    continue

                size = os.path.getsize(hist_db)
                if size < 40960:
                    result.add_warning(f"{browser} [{pname}]: History DB very small ({size} bytes) — possibly cleared")
                    suspicious_found = True

                try:
                    tmp = self._copy_db(hist_db)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM urls")
                    url_count = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM downloads")
                    dl_count = cur.fetchone()[0]
                    conn.close()
                    os.remove(tmp)
                    if url_count == 0:
                        result.add_warning(f"{browser} [{pname}]: Zero history entries — cleared!")
                        suspicious_found = True
                    if dl_count == 0:
                        result.add_warning(f"{browser} [{pname}]: Zero download entries — cleared!")
                        suspicious_found = True
                except Exception as e:
                    result.add_warning(f"Could not read {browser} DB: {e}")

        if not suspicious_found:
            result.add_info("No obvious signs of browser data wiping.")
        return result

    def check_cookies(self):
        result = ForensicsResult()
        for browser, root in BROWSER_PROFILES.items():
            profiles = self._chromium_profiles(root)
            if not profiles:
                continue
            for profile in profiles:
                cookie_db = os.path.join(profile, "Network", "Cookies")
                if not os.path.exists(cookie_db):
                    cookie_db = os.path.join(profile, "Cookies")
                if not os.path.exists(cookie_db):
                    continue
                try:
                    tmp = self._copy_db(cookie_db)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT host_key,
                               datetime(last_access_utc/1000000-11644473600, 'unixepoch', 'localtime')
                        FROM cookies GROUP BY host_key
                        ORDER BY MAX(last_access_utc) DESC LIMIT 60
                    """)
                    for host, ts in cur.fetchall():
                        suspicious = any(k in host.lower() for k in [
                            "crack", "cheat", "hack", "warez", "nulled", "skid",
                            "vape", "sigma", "future", "meteor", "wurst", "ghost",
                            "leaked", "free", "bypass", "inject"
                        ])
                        result.add_entry(
                            browser, os.path.basename(profile), "COOKIE",
                            host, "", ts, suspicious
                        )
                    conn.close()
                    os.remove(tmp)
                except Exception as e:
                    result.add_warning(f"Could not read {browser} cookies: {e}")

        if not result.entries:
            result.add_info("No cookie data found.")
        return result

    def check_cheat_sites(self):
        result = ForensicsResult()

        def is_safe(url):
            return any(safe in url.lower() for safe in SAFE_DOMAINS)

        def is_suspicious(text):
            return any(k in text.lower() for k in CHEAT_SITE_KEYWORDS)

        for browser, root in BROWSER_PROFILES.items():
            profiles = self._chromium_profiles(root)
            for profile in profiles:
                pname = os.path.basename(profile)
                hist_db = os.path.join(profile, "History")
                if not os.path.exists(hist_db):
                    continue
                try:
                    tmp = self._copy_db(hist_db)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT url, title,
                               datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')
                        FROM urls ORDER BY last_visit_time DESC
                    """)
                    for url, title, ts in cur.fetchall():
                        if not is_safe(url) and (is_suspicious(url) or is_suspicious(title or "")):
                            result.add_entry(browser, pname, "HISTORY", url, title or "", ts, True)
                    conn.close()
                    os.remove(tmp)
                except Exception as e:
                    pass

                try:
                    tmp = self._copy_db(hist_db)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT target_path, tab_url,
                               datetime(start_time/1000000-11644473600,'unixepoch','localtime')
                        FROM downloads ORDER BY start_time DESC
                    """)
                    for target, tab_url, ts in cur.fetchall():
                        check_str = (target or "") + (tab_url or "")
                        if not is_safe(check_str) and is_suspicious(check_str):
                            result.add_entry(browser, pname, "DOWNLOAD", tab_url or target,
                                             os.path.basename(target or "?"), ts, True)
                    conn.close()
                    os.remove(tmp)
                except Exception:
                    pass

        if os.path.isdir(FIREFOX_ROOT):
            for profile in os.listdir(FIREFOX_ROOT):
                places = os.path.join(FIREFOX_ROOT, profile, "places.sqlite")
                if not os.path.exists(places):
                    continue
                try:
                    tmp = self._copy_db(places)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT p.url, p.title,
                               datetime(h.visit_date/1000000,'unixepoch','localtime')
                        FROM moz_places p
                        JOIN moz_historyvisits h ON h.place_id = p.id
                        ORDER BY h.visit_date DESC
                    """)
                    for url, title, ts in cur.fetchall():
                        if not is_safe(url) and (is_suspicious(url) or is_suspicious(title or "")):
                            result.add_entry("Firefox", profile, "HISTORY", url, title or "", ts, True)
                    conn.close()
                    os.remove(tmp)
                except Exception as e:
                    pass

        if not result.entries:
            result.add_info("No cheat-related websites found.")
        return result
