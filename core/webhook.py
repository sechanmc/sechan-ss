import json
import urllib.request
import urllib.error
from datetime import datetime
import os


class WebhookSender:
    def __init__(self, url=""):
        self.url = url

    def set_url(self, url):
        self.url = url

    def send_result(self, pin, game, scantime, country, sentence, detects=None):
        if not self.url:
            return False, "No webhook URL configured."

        detects_str = "\n".join(f"\u2022 {d}" for d in (detects or [])) if detects else "None listed"

        embed = {
            "title": "Positive SS Result",
            "color": 0xFF0000,
            "fields": [
                {"name": "PIN",     "value": str(pin),      "inline": True},
                {"name": "Game",    "value": str(game),     "inline": True},
                {"name": "Country", "value": str(country),  "inline": True},
                {"name": "Verdict",   "value": str(sentence), "inline": False},
                {"name": "Scan Time", "value": str(scantime), "inline": False},
                {"name": "Detections", "value": detects_str, "inline": False},
            ],
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + ".000Z",
        }

        return self._post({"embeds": [embed]})

    def send_scan_report(self, results, download_url=""):
        if not self.url:
            return False, "no webhook configured"

        user = os.environ.get("USERNAME", "unknown")
        host = os.environ.get("COMPUTERNAME", "unknown")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_issues = sum(len(r.found) for r in results.values())
        total_warns = sum(len(r.warnings) for r in results.values())

        fields = [
            {"name": "User",   "value": user, "inline": True},
            {"name": "Host",   "value": host, "inline": True},
            {"name": "Date",   "value": now,  "inline": False},
            {"name": "Issues", "value": str(total_issues), "inline": True},
            {"name": "Warnings", "value": str(total_warns), "inline": True},
        ]

        details = []
        for name, r in results.items():
            found_list = [m for m, p in r.found]
            warn_list = [m for m, p in r.warnings]
            if found_list:
                details.append(f"**{name}** - found: {', '.join(found_list[:5])}")
            elif warn_list:
                details.append(f"**{name}** - warnings: {', '.join(warn_list[:5])}")

        if details:
            fields.append({"name": "Details", "value": "\n".join(details[:5])[:1024], "inline": False})

        if download_url:
            fields.append({
                "name": "Download Report",
                "value": f"[download link]({download_url}) \u2022 expires in 15m",
                "inline": False,
            })

        embed = {
            "title": "Sechan SS - Scan Report",
            "color": 0xEF4444 if total_issues > 0 else (0xF59E0B if total_warns > 0 else 0x22C55E),
            "fields": fields,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + ".000Z",
        }

        return self._post({"embeds": [embed]})

    def _post(self, payload_dict):
        payload = json.dumps(payload_dict).encode("utf-8")
        try:
            req = urllib.request.Request(
                self.url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return True, f"sent (status {resp.status})"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            return False, f"HTTP {e.code}: {body[:200]}"
        except Exception as e:
            return False, f"failed: {e}"
