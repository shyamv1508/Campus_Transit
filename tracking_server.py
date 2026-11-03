"""Local HTTP server for the live bus map and driver GPS updates."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json

import database

ROOT = Path(__file__).parent
HOST, PORT = "127.0.0.1", 8765


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/locations":
            self._send(200, json.dumps(database.latest_locations()))
            return
        pages = {"/map": "map.html", "/driver": "driver.html"}
        if path in pages:
            page = ROOT / "templates" / pages[path]
            if page.exists():
                self._send(200, page.read_text(encoding="utf-8"), "text/html; charset=utf-8")
                return
        self._send(404, json.dumps({"error": "Not found"}))

    def do_POST(self):
        if urlparse(self.path).path != "/api/location":
            self._send(404, json.dumps({"error": "Not found"}))
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 4096:
                raise ValueError("Invalid request size")
            payload = json.loads(self.rfile.read(length))
            bus_id = int(payload["bus_id"])
            lat, lon = float(payload["latitude"]), float(payload["longitude"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("Coordinates out of range")
            database.save_location(bus_id, lat, lon)
            self._send(200, json.dumps({"ok": True}))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, json.dumps({"error": str(exc)}))

    def log_message(self, _format, *_args):
        pass


def run_server():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    database.init_db()
    print(f"Campus Transit tracking server: http://{HOST}:{PORT}/map")
    run_server()
