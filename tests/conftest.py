import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

os.environ.setdefault("AUTOPPIA_BOOTSTRAP_DISABLE", "1")

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def stub_agent():
    class StubAgent:
        def __init__(self):
            self.actions = []
            self.base_url: str | None = None
            self._server: HTTPServer | None = None
            self._thread: threading.Thread | None = None

        def start(self):
            parent = self

            class Handler(BaseHTTPRequestHandler):
                def do_POST(self):
                    if self.path != "/solve_task":
                        self.send_response(404)
                        self.end_headers()
                        return
                    length = int(self.headers.get("content-length", "0"))
                    if length:
                        self.rfile.read(length)
                    body = json.dumps({"actions": parent.actions, "web_agent_id": "stub-agent"}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

                def log_message(self, format, *args):
                    return

            server = HTTPServer(("127.0.0.1", 0), Handler)
            self.base_url = f"http://127.0.0.1:{server.server_address[1]}"
            self._server = server
            self._thread = threading.Thread(target=server.serve_forever, daemon=True)
            self._thread.start()

        def close(self):
            if self._server:
                self._server.shutdown()
                if self._thread:
                    self._thread.join()
                self._server.server_close()
                self._server = None
                self._thread = None

    stub = StubAgent()
    stub.start()
    try:
        yield stub
    finally:
        stub.close()


collect_ignore_glob = ["_deprecated/*.py"]
