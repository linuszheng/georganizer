#!/usr/bin/env python3
"""Simple HTTP server that serves static files and handles flyer data read/write."""

import http.server
import json
import os

PORT = 8000
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flyer-data.json")

class Handler(http.server.SimpleHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/flyers':
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            self._send_json(200, data)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/flyers':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                self._send_json(200, {"ok": True})
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid json"})
        else:
            self._send_json(404, {"error": "not found"})

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Serving on http://localhost:{PORT}")
http.server.HTTPServer(('', PORT), Handler).serve_forever()
