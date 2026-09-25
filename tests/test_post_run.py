"""A lifecycle run is only on record once Anvil holds it; posting must say so
loudly when it does not happen."""

import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "post_run.py"


@pytest.fixture
def anvil():
    calls = []
    state = {"fail_patch": False, "no_run_id": False}

    class Handler(BaseHTTPRequestHandler):
        def _body(self):
            n = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(n) or b"{}")

        def do_POST(self):
            calls.append(("POST", self.path, self._body()))
            self.send_response(201)
            self.end_headers()
            body = {} if state["no_run_id"] else {"run_id": "lifecycle-srv-1"}
            self.wfile.write(json.dumps(body).encode())

        def do_PATCH(self):
            calls.append(("PATCH", self.path, self._body()))
            self.send_response(500 if state["fail_patch"] else 200)
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *a):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}", calls, state
    server.shutdown()


def run(url, run_file):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(run_file), "--anvil-url", url],
        capture_output=True,
        text=True,
        check=False,
    )


def write_run(tmp_path, **over):
    data = {
        "trigger": "manual",
        "skipped_phases": [],
        "status": "completed",
        "completed_at": "2026-09-25T10:00:00+08:00",
        "total_skills": 118,
        "optimized": 1,
        "changes_applied": 4,
        "phases": {"audit": {"clusters": 2}},
        "errors": {},
    }
    data.update(over)
    f = tmp_path / "run.json"
    f.write_text(json.dumps(data))
    return f


def test_creates_then_fills_the_run(anvil, tmp_path):
    url, calls, _ = anvil
    r = run(url, write_run(tmp_path))
    assert r.returncode == 0, r.stderr
    assert "lifecycle-srv-1" in r.stdout
    assert [c[:2] for c in calls] == [
        ("POST", "/api/anvil/lifecycle/runs"),
        ("PATCH", "/api/anvil/lifecycle/runs/lifecycle-srv-1"),
    ]
    assert calls[0][2] == {"trigger": "manual", "skipped_phases": []}
    patch = calls[1][2]
    assert patch["optimized"] == 1 and patch["changes_applied"] == 4
    assert patch["phases"] == {"audit": {"clusters": 2}}


def test_a_failed_update_exits_nonzero(anvil, tmp_path):
    url, _, state = anvil
    state["fail_patch"] = True
    r = run(url, write_run(tmp_path))
    assert r.returncode != 0
    assert "lifecycle-srv-1" in r.stderr


def test_an_unreachable_anvil_exits_nonzero(tmp_path):
    r = run("http://127.0.0.1:9", write_run(tmp_path))
    assert r.returncode != 0


def test_missing_required_fields_are_rejected_before_any_call(anvil, tmp_path):
    url, calls, _ = anvil
    f = tmp_path / "run.json"
    f.write_text(json.dumps({"trigger": "manual"}))
    r = run(url, f)
    assert r.returncode != 0
    assert calls == []


def test_unknown_fields_are_refused_before_any_call(anvil, tmp_path):
    url, calls, _ = anvil
    r = run(url, write_run(tmp_path, publishd=2))
    assert r.returncode != 0
    assert "publishd" in r.stderr
    assert calls == []


def test_a_create_response_without_run_id_exits_cleanly(anvil, tmp_path):
    url, calls, state = anvil
    state["no_run_id"] = True
    r = run(url, write_run(tmp_path))
    assert r.returncode == 1
    assert "Traceback" not in r.stderr
    assert [c[0] for c in calls] == ["POST"]
