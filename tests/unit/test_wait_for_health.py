"""Tests for ci/wait_for_health.py, the Deploy stage's health check (Role D)."""

import http.server
import importlib.util
import json
import threading
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "wait_for_health", Path(__file__).resolve().parents[2] / "ci" / "wait_for_health.py"
)
wfh = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(wfh)


def test_url_is_always_local_health_endpoint():
    assert wfh.health_url(8000) == "http://127.0.0.1:8000/health"


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_out_of_range_port_is_rejected(port):
    with pytest.raises(ValueError, match="port must be between"):
        wfh.health_url(port)


@pytest.fixture
def health_server():
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = json.dumps({"status": "ok"}).encode()
            self.send_response(200 if self.path == "/health" else 404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield server.server_address[1]
    server.shutdown()


def test_returns_true_when_health_answers_ok(health_server):
    assert wfh.wait_for_health(health_server, timeout_s=5, interval_s=0.1)


def test_returns_false_when_nothing_answers():
    # Port 9 (discard) is not listening on a normal machine, so every attempt fails.
    assert not wfh.wait_for_health(9, timeout_s=0.3, interval_s=0.1)
