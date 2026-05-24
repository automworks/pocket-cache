#!/usr/bin/env python3
"""
Minimal portal web server for pocket-cache.
Serves static portal files and exposes /api/status with live device data.
Replaces 'python -m http.server 80' in the systemd service.

Usage:
    python3 portal/server.py [--port 80] [--bind 0.0.0.0]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

_PORTAL_DIR = Path(__file__).parent
_CONFIG_PATH = Path(os.environ.get("POCKETCACHE_CONFIG", "/etc/pocket-cache/firmware.json"))
_START_TIME = time.time()


def _read_config() -> dict:
    try:
        return json.loads(_CONFIG_PATH.read_text())
    except Exception:
        return {"ssid": "PocketCache", "ip_address": "10.0.0.1", "portal_url": "http://10.0.0.1"}


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, timeout=3).strip()
    except Exception:
        return ""


def _get_status() -> dict:
    cfg = _read_config()

    uptime_s = int(time.time() - _START_TIME)
    h, remainder = divmod(uptime_s, 3600)
    m, s = divmod(remainder, 60)
    uptime_str = f"{h}h {m}m" if h else f"{m}m {s}s"

    # CPU temperature (Pi-specific; graceful fallback)
    temp_raw = _run(["vcgencmd", "measure_temp"])
    temp = temp_raw.replace("temp=", "").replace("'C", "") if temp_raw else "N/A"

    # Disk usage for portal directory
    df_raw = _run(["df", "-h", str(_PORTAL_DIR)])
    df_line = df_raw.splitlines()[-1].split() if df_raw else []
    disk_used = df_line[2] if len(df_line) > 4 else "N/A"
    disk_total = df_line[1] if len(df_line) > 4 else "N/A"

    # Client count from arp table (devices seen on wlan0)
    arp_raw = _run(["arp", "-n", "-i", "wlan0"])
    clients = max(0, len(arp_raw.splitlines()) - 1) if arp_raw else 0

    return {
        "ssid": cfg.get("ssid", "PocketCache"),
        "ip": cfg.get("ip_address", "10.0.0.1"),
        "portal_url": cfg.get("portal_url", "http://10.0.0.1"),
        "uptime": uptime_str,
        "cpu_temp": temp,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "clients": clients,
        "mode": "offline",
    }


_MIME = {
    ".html": "text/html; charset=utf-8",
    ".css":  "text/css",
    ".js":   "application/javascript",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".ico":  "image/x-icon",
    ".json": "application/json",
    ".txt":  "text/plain; charset=utf-8",
}


class PortalHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress default access log noise
        pass

    def do_GET(self):
        # Captive portal redirect: OS probes (iOS, Android, Windows) arrive with a
        # Host header pointing at an external domain. Redirect them to hello.html so
        # the OS captive portal sheet opens automatically after joining the hotspot.
        host = self.headers.get("Host", "")
        if not host.startswith("10.0.0.1"):
            self.send_response(302)
            self.send_header("Location", "http://10.0.0.1/hello.html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        path = urlparse(self.path).path

        # Live status API
        if path == "/api/status":
            body = json.dumps(_get_status(), indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        # Normalize path to file
        if path == "/" or path == "":
            path = "/index.html"
        file_path = _PORTAL_DIR / path.lstrip("/")

        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "Not Found")
            return

        suffix = file_path.suffix.lower()
        mime = _MIME.get(suffix, "application/octet-stream")
        data = file_path.read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    parser = argparse.ArgumentParser(description="pocket-cache portal server")
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--bind", default="0.0.0.0")
    args = parser.parse_args()

    server = HTTPServer((args.bind, args.port), PortalHandler)
    print(f"pocket-cache portal listening on {args.bind}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
