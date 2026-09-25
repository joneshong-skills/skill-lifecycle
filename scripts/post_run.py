#!/usr/bin/env python3
"""Record a lifecycle run in Anvil, the same table the weekly cron writes to.

Usage:
    post_run.py run.json [--anvil-url http://127.0.0.1:10301]

run.json carries the LifecycleRunCreate/Update fields: trigger, skipped_phases,
status, completed_at, total_skills, optimized, changes_applied, phases, errors
(plus any other field the Anvil update model accepts). Anvil assigns run_id and
started_at when the run is created, so put the local run id and real start time
inside "phases".

Exits non-zero whenever the run did not land in Anvil: a report that says
"recorded" while nothing was written is the failure this step exists to prevent.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REQUIRED = ("trigger", "status", "completed_at", "phases")


def call(method: str, url: str, body: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read() or b"{}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a lifecycle run in Anvil")
    parser.add_argument("run_file", type=Path)
    parser.add_argument("--anvil-url", default="http://127.0.0.1:10301")
    args = parser.parse_args()

    run = json.loads(args.run_file.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in run]
    if missing:
        print(f"run file is missing: {', '.join(missing)}", file=sys.stderr)
        return 1

    base = f"{args.anvil_url.rstrip('/')}/api/anvil/lifecycle/runs"
    try:
        created = call(
            "POST",
            base,
            {
                "trigger": run["trigger"],
                "skipped_phases": run.get("skipped_phases", []),
            },
        )
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"Anvil did not accept the run: {e}", file=sys.stderr)
        return 1

    run_id = created["run_id"]
    update = {k: v for k, v in run.items() if k != "trigger"}
    try:
        call("PATCH", f"{base}/{run_id}", update)
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(
            f"Created {run_id} but could not fill in its results: {e}", file=sys.stderr
        )
        return 1

    print(f"Recorded in Anvil: {run_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
