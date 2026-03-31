"""
server.py
---------
Mini HTTP server untuk Web UI viewer reqtrace.

Menyediakan:
- Static file serving (index.html)
- REST endpoint untuk membaca log file (/api/logs)
- SSE endpoint untuk real-time update (/api/stream)
"""

import json
import os
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


STATIC_DIR = Path(__file__).parent / "static"


def _read_logs(file_path: str) -> list[dict]:
    """Baca semua log dari NDJSON file."""
    logs = []
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except FileNotFoundError:
        pass
    return logs


def _get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        return 0


class ViewerHandler(BaseHTTPRequestHandler):
    """HTTP request handler untuk viewer."""

    # di-set oleh start_viewer sebelum server jalan
    log_file: str = ""

    def log_message(self, format, *args) -> None:
        # suppress default server log agar tidak berisik di terminal
        pass

    def do_GET(self) -> None:
        if self.path == "/" or self.path == "/index.html":
            self._serve_static("index.html")
        elif self.path == "/api/logs":
            self._serve_logs()
        elif self.path == "/api/stream":
            self._serve_sse()
        elif self.path == "/api/info":
            self._serve_info()
        else:
            self._send_404()

    # ------------------------------------------------------------------
    # handlers
    # ------------------------------------------------------------------

    def _serve_static(self, filename: str) -> None:
        path = STATIC_DIR / filename
        if not path.exists():
            self._send_404()
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _serve_logs(self) -> None:
        logs = _read_logs(self.log_file)
        body = json.dumps(logs, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_info(self) -> None:
        info = {
            "file": self.log_file,
            "version": "0.4.0",
        }
        body = json.dumps(info).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_sse(self) -> None:
        """
        Server-Sent Events endpoint.
        Poll file setiap 1 detik, kirim event jika ada baris baru.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        last_size = _get_file_size(self.log_file)

        try:
            while True:
                time.sleep(1)
                current_size = _get_file_size(self.log_file)

                if current_size > last_size:
                    # baca baris baru saja
                    new_logs = self._read_new_lines(last_size)
                    for log in new_logs:
                        data = json.dumps(log, ensure_ascii=False)
                        msg = f"data: {data}\n\n"
                        self.wfile.write(msg.encode("utf-8"))
                        self.wfile.flush()
                    last_size = current_size

                # heartbeat agar koneksi tidak timeout
                self.wfile.write(b": heartbeat\n\n")
                self.wfile.flush()

        except (BrokenPipeError, ConnectionResetError):
            pass

    def _read_new_lines(self, from_byte: int) -> list[dict]:
        """Baca baris baru mulai dari posisi byte tertentu."""
        new_logs = []
        try:
            with open(self.log_file, encoding="utf-8") as f:
                f.seek(from_byte)
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            new_logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            pass
        return new_logs

    def _send_404(self) -> None:
        self.send_response(404)
        self.end_headers()


def start_viewer(file_path: str, port: int = 8765, open_browser: bool = True) -> None:
    """
    Start Web UI viewer server.
    Blocks until CTRL+C.
    """
    # inject log_file ke handler class
    ViewerHandler.log_file = os.path.abspath(file_path)

    server = HTTPServer(("localhost", port), ViewerHandler)
    url = f"http://localhost:{port}"

    print(f"[reqtrace] Web UI viewer running at {url}")
    print(f"[reqtrace] Reading log file: {file_path}")
    print(f"[reqtrace] Press CTRL+C to stop\n")

    if open_browser:
        # buka browser setelah server siap (delay kecil)
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[reqtrace] Viewer stopped.")
        server.shutdown()
