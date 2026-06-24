import os
import socket
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler


class _SingleFileHandler(BaseHTTPRequestHandler):
    file_path = ""
    filename = ""

    def do_GET(self):
        if self.path == "/" + self.filename:
            try:
                with open(self.file_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{self.filename}"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except Exception:
                self.send_error(500, "server error")
        else:
            self.send_error(404, "not found")

    def log_message(self, fmt, *args):
        pass


class TempFileServer:
    def __init__(self):
        self.server = None
        self.thread = None
        self.url = ""
        self._port = 0

    def start(self, file_path, lifetime=900):
        self._port = self._find_port()
        filename = os.path.basename(file_path)
        _SingleFileHandler.file_path = file_path
        _SingleFileHandler.filename = filename

        self.server = HTTPServer(("0.0.0.0", self._port), _SingleFileHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        ip = self._get_local_ip()
        self.url = f"http://{ip}:{self._port}/{filename}"

        threading.Thread(target=self._auto_kill, args=(lifetime,), daemon=True).start()

        return self.url

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def _auto_kill(self, delay):
        time.sleep(delay)
        self.stop()

    def _find_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
