#!/usr/bin/env python3
"""Dependency-free development server for the demo application."""

from __future__ import annotations

import json
import random
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
HOST = "127.0.0.1"
PORT = 8080


def generate_license(state: str, first_name: str, last_name: str) -> str:
    state = state.strip().upper()
    first = (first_name.strip()[:1] or "X").upper()
    last = (last_name.strip()[:1] or "X").upper()
    return f"{state}-{first}{last}-{random.randint(0, 999999):06d}"


def validate_license(state: str, value: str) -> bool:
    state = state.strip().upper()
    return bool(re.fullmatch(rf"{re.escape(state)}-[A-Z]{{2}}-\d{{6}}", value.strip().upper()))


class Handler(BaseHTTPRequestHandler):
    server_version = "DriverLicenseDemo/1.0"

    def _send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "请求必须是有效 JSON"})
            return

        path = urlparse(self.path).path
        if path == "/generate":
            self._send_json(200, {"licenseNumber": generate_license(
                str(payload.get("state", "")),
                str(payload.get("firstName", "")),
                str(payload.get("lastName", "")),
            )})
            return
        if path == "/validate":
            self._send_json(200, {"valid": validate_license(
                str(payload.get("state", "")),
                str(payload.get("licenseNumber", "")),
            )})
            return
        self._send_json(404, {"error": "接口不存在"})

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        relative = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (FRONTEND / relative).resolve()
        if FRONTEND not in target.parents and target != FRONTEND:
            self.send_error(403)
            return
        if not target.is_file():
            self.send_error(404)
            return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".svg": "image/svg+xml",
        }.get(target.suffix, "application/octet-stream")
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")


if __name__ == "__main__":
    print(f"开发服务器已启动: http://{HOST}:{PORT}")
    print("仅用于演示和测试，生成内容不是有效证件。")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
