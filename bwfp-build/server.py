"""Local dev server for the BWFP live service.

Runs the same service core the Vercel functions run (bwfp/service.py),
on your own machine, so you can check the API before deploying.

Usage:
    python3 server.py            # serves on http://localhost:8000
    PORT=9000 python3 server.py  # another port

Then:
    curl http://localhost:8000/api/identity
    curl -X POST http://localhost:8000/api/task \
        -H 'Content-Type: application/json' \
        -d '{"task": "Summarize what the three identities in Layer 1 are."}'

With no GROQ_API_KEY set, the service still answers: the control
layer runs on its own and the response says plainly that no live
model is attached. To attach the live brain, set the key first:
    GROQ_API_KEY=... python3 server.py
The key is read from the environment only. Never paste it here.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bwfp.service import handle_task, identity_payload


class LocalHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self):
        self._send_json(404, {"error": "not found - use /api/identity or /api/task"})

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/api/identity":
            self._send_json(200, identity_payload())
            return
        if path == "/api/task":
            query = parse_qs(urlparse(self.path).query)
            task = (query.get("task") or query.get("request") or [""])[0]
            status, payload = handle_task(task)
            self._send_json(status, payload)
            return
        self._not_found()

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path != "/api/task":
            self._not_found()
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = raw.decode("utf-8", "replace")
        status, payload = handle_task(body)
        self._send_json(status, payload)

    def log_message(self, *args):
        sys.stderr.write("[bwfp-live] %s %s\n" % (self.command, self.path))


def main():
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), LocalHandler)
    key = "set" if os.environ.get("GROQ_API_KEY") else "NOT set (control layer only)"
    print(f"BWFP live service on http://127.0.0.1:{port}")
    print("  /api/identity   /api/task")
    print(f"  GROQ_API_KEY: {key}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
