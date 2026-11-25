"""Vercel serverless function: /api/task.

Takes a request, runs it through the BWFP six-layer pipeline, and
returns the answer — or the halt with the reasoned why.

  POST /api/task   JSON body: {"task": "..."}  (or {"request": "..."})
  GET  /api/task?task=...

The Groq key comes from GROQ_API_KEY only. If it is not set, the
service still runs and says so plainly in the response.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bwfp.service import handle_task


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        task = (query.get("task") or query.get("request") or [""])[0]
        status, payload = handle_task(task)
        self._send(status, payload)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = raw.decode("utf-8", "replace")
        status, payload = handle_task(body)
        self._send(status, payload)

    def log_message(self, *args):
        pass
