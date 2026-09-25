"""The report has to say what the run did: the phases SKILL.md defines, and
notes that annotate a phase without turning it into a failure."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lifecycle_report.py"


def report(*args):
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--run-id", "t", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    return r.stdout


def status_row(text, phase):
    return next(line for line in text.splitlines() if line.startswith(f"| {phase} |"))


def test_only_the_skill_md_phases_are_reported():
    text = report()
    assert "Security" not in text
    assert "security" not in text
    assert "4/4" in text


def test_a_note_keeps_the_phase_ok_and_its_metrics():
    text = report(
        "--published",
        "2",
        "--logos",
        "1",
        "--note",
        "publish:push confirmed at the prompt, then verified with git fetch",
    )
    assert status_row(text, "Publish").endswith("| OK |")
    assert "| Skills published | 2 |" in text
    assert "push confirmed at the prompt, then verified with git fetch" in text
    assert "FAILED" not in text


def test_notes_repeat_and_keep_commas():
    text = report(
        "--note",
        "catalog:ran the archived scan, 3358 edges",
        "--note",
        "audit:1 false positive, ignored",
    )
    assert "ran the archived scan, 3358 edges" in text
    assert "1 false positive, ignored" in text


def test_errors_still_fail_the_phase():
    text = report("--errors", "optimize:timeout on skill-foo")
    assert status_row(text, "Optimize").endswith("| FAILED |")
    assert "timeout on skill-foo" in text


def test_generate_accepts_notes():
    sys.path.insert(0, str(SCRIPT.parent))
    import lifecycle_report

    text = lifecycle_report.generate(
        run_id="t", published=1, notes=["publish:verified remote"]
    )
    assert "verified remote" in text
    assert status_row(text, "Publish").endswith("| OK |")
