import json
import os
import uuid
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def _build_multipart(fields, file_path):
    boundary = uuid.uuid4().hex
    body = bytearray()
    crlf = b"\r\n"

    for key, value in fields.items():
        body += f"--{boundary}{crlf}".encode()
        body += f'Content-Disposition: form-data; name="{key}"{crlf}{crlf}'.encode()
        body += f"{value}{crlf}".encode()

    if file_path:
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            file_data = f.read()
        body += f"--{boundary}{crlf}".encode()
        body += f'Content-Disposition: form-data; name="file"; filename="{filename}"{crlf}'.encode()
        body += b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
        body += file_data
        body += crlf

    body += f"--{boundary}--{crlf}".encode()
    content_type = f"multipart/form-data; boundary={boundary}"
    return bytes(body), content_type


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

    def send_scan_report(self, results, report_path=""):
        if not self.url:
            return False, "no webhook configured"

        user = os.environ.get("USERNAME", "unknown")
        host = os.environ.get("COMPUTERNAME", "unknown")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_issues = sum(len(r.found) for r in results.values())
        total_warns = sum(len(r.warnings) for r in results.values())

        attachments = []
        if report_path and os.path.exists(report_path):
            filename = os.path.basename(report_path)
            attachments.append({"id": 0, "filename": filename})

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

        if attachments:
            fields.append({
                "name": "Report",
                "value": f"attached: {attachments[0]['filename']}",
                "inline": False,
            })

        payload = {
            "embeds": [{
                "title": "Sechan SS - Scan Report",
                "color": 0xEF4444 if total_issues > 0 else (0xF59E0B if total_warns > 0 else 0x22C55E),
                "fields": fields,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + ".000Z",
            }],
            "attachments": attachments,
        }

        if report_path and os.path.exists(report_path):
            multipart_fields = {"payload_json": json.dumps(payload)}
            data, content_type = _build_multipart(multipart_fields, report_path)
            return self._post_raw(data, content_type)
        else:
            return self._post(payload)

    def _post(self, payload_dict):
        data = json.dumps(payload_dict).encode("utf-8")
        return self._post_raw(data, "application/json")

    def _post_raw(self, data, content_type):
        try:
            req = Request(
                self.url,
                data=data,
                headers={
                    "Content-Type": content_type,
                    "User-Agent": "Mozilla/5.0",
                },
                method="POST",
            )
            with urlopen(req, timeout=15) as resp:
                return True, f"sent (status {resp.status})"
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            return False, f"HTTP {e.code}: {body[:300]}"
        except Exception as e:
            return False, f"failed: {e}"
