#!/usr/bin/env python3
"""Simple static-file web server for the work-2 host (port 12001."""

import json
import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
STARTED = time.time()


def runtime_id_for(host):
    host = host.lower()
    if host.startswith("work-2-wxniqlsnuptzpymt"):
        return "wxniqlsnuptzpymt"
    if host.startswith("work-2-aftnxdqtpgjwydap"):
        return "aftnxdqtpgjwydap"
    return "runtime"


def uptime_str():
    return str(time.time() - STARTED)[:6]


class Handler(BaseHTTPRequestHandler):
    server_version = "Work2Server/1.0"

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(parsed.path)
        rid = runtime_id_for(self.headers.get("Host", ""))

        if path == "/health" or path == "/healthz":
            data = {"status": "ok", "host": rid, "port": 12001}
            data["uptime_s"] = uptime_str()
            self._send_json(data)
            return

        if path == "/status":
            data = {
                "status": "running",
                "server": "Work2Server",
                "runtime_id": rid,
                "port": 12001,
                "url": "https://work-2-wxniqlsnuptzpymt.prod-runtime.all-hands.dev/",
            }
            data["uptime_s"] = uptime_str()
            self._send_json(data)
            return

        if path in ("/", "/index.html"):
            self._serve_file(os.path.join(ROOT, "index.html"), "text/html; charset=utf-8")
            return

        if path in ("/work2", "/work2/"):
            self._serve_file(os.path.join(ROOT, "work2.html"), "text/html; charset=utf-8")
            return

        self._send(404, "text/plain; charset=utf-8", b"page not found")

    def _send_json(self, obj):
        body = json.dumps(obj)
        self._send(200, "application/json", body.encode())

    def log_message(self, format, *args):
        print("[%s] %s" % (self.log_date_time_string(), format % args))

    def _serve_file(self, fspath, content_type):
        try:
            with open(fspath, "rb") as f:
                data = f.read()
            self._send(200, content_type, data)
        except FileNotFoundError:
            self._send(404, "text/plain; charset=utf-8", b"page not found")

    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Work2-Status", "running")
        self.end_headers()
        self.wfile.write(body)

def main():
    port = int(os.environ.get("PORT", "12001"))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    httpd.daemon_threads = True
    print(f"Work2 server listening on 0.0.0.0:{port}", flush=True)
    httpd.serve_forever()

if __name__ == "__main__":
    main()