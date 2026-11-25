"""Vercel serverless function: GET /api/identity.

Who this system is, what it is, whether the live brain is attached.
Same shape as the live Agent 1 service.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bwfp.service import identity_payload


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = json.dumps(identity_payload()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
