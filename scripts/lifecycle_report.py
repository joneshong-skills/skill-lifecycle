#!/usr/bin/env python3
"""Generate a markdown summary report for a skill-lifecycle pipeline run.

Usage:
    python3 lifecycle_report.py \
        --run-id "lifecycle-20260212-143000" \
        --audit-merges 2 --audit-splits 0 --audit-retires 1 \
        --tested 10 --test-passed 8 --test-partial 1 --test-failed 1 \
        --sec-clean 9 --sec-warned 1 --sec-blocked 0 \
        --optimized 3 --unchanged 5 --changes 7 \
        --published 4 --repos-created 1 --readmes 4 --logos 2 \
        --total-skills 30 --total-edges 45 \
        [--skipped-phases "audit,publish"] \
        [--errors "optimize:timeout on skill-foo,publish:git auth failed"] \
        [-o ~/Downloads/lifecycle-report-20260228.md]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def parse_key_value_list(raw: Optional[str]) -> List[Tuple[str, str]]:
    """Parse 'key:value,key:value' into list of tuples."""
    if not raw or raw.strip() == "":
        return []
    pairs = []
    for item in raw.split(","):
        item = item.strip()
        if ":" in item:
            k, v = item.split(":", 1)
            pairs.append((k.strip(), v.strip()))
        else:
            pairs.append((item, ""))
    return pairs


def parse_list(raw: Optional[str]) -> List[str]:
    """Parse 'a,b,c' into list of strings."""
    if not raw or raw.strip() == "":
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def phase_status_emoji(phase: str, skipped: List[str], errors: Dict[str, str]) -> str:
    """Return a status indicator for each phase."""
    if phase in skipped:
        return "SKIPPED"
    if phase in errors:
        return "FAILED"
    return "OK"


def build_report(args: argparse.Namespace) -> str:
    """Build the full markdown report."""
    skipped = parse_list(args.skipped_phases)
    errors = dict(parse_key_value_list(args.errors))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    # Header
    lines.append("# Skill Lifecycle Report")
    lines.append("")
    lines.append(f"**Run ID:** `{args.run_id}`")
    lines.append(f"**Generated:** {now}")
    lines.append("")

    # Pipeline Status Overview
    lines.append("## Pipeline Status")
    lines.append("")
    lines.append("| Phase | Sub-Skill | Gate | Status |")
    lines.append("|-------|-----------|------|--------|")

    phases = [
        ("audit", "skill-curator", "—"),
        ("test", "skill-tester", "—"),
        ("security", "skill-security-scan", "HARD"),
        ("optimize", "skill-optimizer", "—"),
        ("publish", "skill-publisher", "—"),
        ("catalog", "skill-catalog", "—"),
    ]
    for phase, skill, gate in phases:
        status = phase_status_emoji(phase, skipped, errors)
        lines.append(f"| {phase.capitalize()} | {skill} | {gate} | {status} |")
    lines.append("")

    # Phase 1: Audit
    lines.append("## Phase 1: Audit")
    lines.append("")
    if "audit" in skipped:
        lines.append("*Phase skipped by user.*")
    elif "audit" in errors:
        lines.append(f"*Phase failed:* {errors['audit']}")
    else:
        total_audit_actions = args.audit_merges + args.audit_splits + args.audit_retires
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Skills merged | {args.audit_merges} |")
        lines.append(f"| Skills split | {args.audit_splits} |")
        lines.append(f"| Skills retired | {args.audit_retires} |")
        lines.append(f"| **Total actions** | **{total_audit_actions}** |")
    lines.append("")

    # Phase 2: Test
    lines.append("## Phase 2: Test")
    lines.append("")
    if "test" in skipped:
        lines.append("*Phase skipped by user.*")
    elif "test" in errors:
        lines.append(f"*Phase failed:* {errors['test']}")
    else:
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Skills tested | {args.tested} |")
        lines.append(f"| Passed | {args.test_passed} |")
        lines.append(f"| Partial | {args.test_partial} |")
        lines.append(f"| Failed | {args.test_failed} |")
    lines.append("")

    # Phase 3: Security Scan (HARD GATE)
    lines.append("## Phase 3: Security Scan (HARD GATE)")
    lines.append("")
    if "security" in skipped:
        lines.append("*Phase skipped by user.*")
    elif "security" in errors:
        lines.append(f"*Phase failed:* {errors['security']}")
    else:
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Skills clean (PASS) | {args.sec_clean} |")
        lines.append(f"| Skills warned (WARN) | {args.sec_warned} |")
        lines.append(f"| Skills blocked (BLOCK) | {args.sec_blocked} |")
        if args.sec_blocked > 0:
            lines.append("")
            lines.append(f"**{args.sec_blocked} skill(s) BLOCKED** — removed from pipeline, require manual remediation.")
    lines.append("")

    # Phase 4: Optimize
    lines.append("## Phase 4: Optimize")
    lines.append("")
    if "optimize" in skipped:
        lines.append("*Phase skipped by user.*")
    elif "optimize" in errors:
        lines.append(f"*Phase failed:* {errors['optimize']}")
    else:
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Skills optimized | {args.optimized} |")
        lines.append(f"| Skills unchanged | {args.unchanged} |")
        lines.append(f"| Total changes applied | {args.changes} |")
    lines.append("")

    # Phase 5: Publish
    lines.append("## Phase 5: Publish")
    lines.append("")
    if "publish" in skipped:
        lines.append("*Phase skipped by user.*")
    elif "publish" in errors:
        lines.append(f"*Phase failed:* {errors['publish']}")
    else:
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Skills published | {args.published} |")
        lines.append(f"| New repos created | {args.repos_created} |")
        lines.append(f"| READMEs generated | {args.readmes} |")
        lines.append(f"| Logos generated | {args.logos} |")
    lines.append("")

    # Phase 6: Catalog
    lines.append("## Phase 6: Catalog")
    lines.append("")
    if "catalog" in skipped:
        lines.append("*Phase skipped by user.*")
    elif "catalog" in errors:
        lines.append(f"*Phase failed:* {errors['catalog']}")
    else:
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total skills | {args.total_skills} |")
        lines.append(f"| Total edges | {args.total_edges} |")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")

    completed = [p for p, _, _ in phases if p not in skipped and p not in errors]
    failed = [p for p in errors if p not in skipped]
    total_phases = len(phases)

    lines.append(f"- **Phases completed:** {len(completed)}/{total_phases} ({', '.join(completed) if completed else 'none'})")
    if skipped:
        lines.append(f"- **Phases skipped:** {', '.join(skipped)}")
    if failed:
        lines.append(f"- **Phases failed:** {', '.join(failed)}")

    # Net change summary
    if "audit" not in skipped and "audit" not in errors:
        net = args.audit_merges + args.audit_retires - args.audit_splits
        if net > 0:
            lines.append(f"- **Net skill reduction:** {net} (from merges/retires)")
        elif net < 0:
            lines.append(f"- **Net skill increase:** {abs(net)} (from splits)")

    if "security" not in skipped and "security" not in errors and args.sec_blocked > 0:
        lines.append(f"- **Skills blocked by security:** {args.sec_blocked} (require manual fix)")

    if "optimize" not in skipped and "optimize" not in errors and args.changes > 0:
        lines.append(f"- **Optimization changes:** {args.changes} across {args.optimized} skills")

    lines.append("")

    # Errors section
    if errors:
        lines.append("## Errors")
        lines.append("")
        for phase, message in errors.items():
            lines.append(f"- **{phase.capitalize()}:** {message}")
        lines.append("")

        lines.append("### Retry Commands")
        lines.append("")
        retry_map = {
            "audit": "`/skill-curator`",
            "test": "`/skill-tester`",
            "security": "`python3 ~/.claude/skills/skill-security-scan/scripts/security-scan.py --batch`",
            "optimize": "`/skill-optimizer [skill-name]`",
            "publish": "`/skill-publisher --all`",
            "catalog": "`/skill-catalog`",
        }
        for phase in errors:
            if phase in retry_map:
                lines.append(f"- {phase.capitalize()}: {retry_map[phase]}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("*Report generated by skill-lifecycle v0.4.0*")

    return "\n".join(lines)


# --- Programmatic API for sandbox_execute ---

def generate(run_id: str, **kwargs) -> str:
    """Generate report programmatically (for sandbox_execute imports).

    Example:
        import lifecycle_report
        report = lifecycle_report.generate(
            run_id='lifecycle-20260228-120000',
            audit_merges=2, audit_splits=0, audit_retires=1,
            tested=10, test_passed=8, test_partial=1, test_failed=1,
            sec_clean=9, sec_warned=1, sec_blocked=0,
            optimized=3, unchanged=5, changes=7,
            published=4, repos_created=1, readmes=4, logos=2,
            total_skills=30, total_edges=45,
        )
    """
    defaults = dict(
        run_id=run_id,
        audit_merges=0, audit_splits=0, audit_retires=0,
        tested=0, test_passed=0, test_partial=0, test_failed=0,
        sec_clean=0, sec_warned=0, sec_blocked=0,
        optimized=0, unchanged=0, changes=0,
        published=0, repos_created=0, readmes=0, logos=0,
        total_skills=0, total_edges=0,
        skipped_phases="", errors="",
    )
    defaults.update(kwargs)

    ns = argparse.Namespace(**defaults)
    return build_report(ns)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a lifecycle pipeline report in markdown."
    )
    parser.add_argument("--run-id", required=True, help="Unique run identifier")

    # Audit metrics
    parser.add_argument("--audit-merges", type=int, default=0, help="Skills merged in audit")
    parser.add_argument("--audit-splits", type=int, default=0, help="Skills split in audit")
    parser.add_argument("--audit-retires", type=int, default=0, help="Skills retired in audit")

    # Test metrics
    parser.add_argument("--tested", type=int, default=0, help="Total skills tested")
    parser.add_argument("--test-passed", type=int, default=0, help="Skills that passed tests")
    parser.add_argument("--test-partial", type=int, default=0, help="Skills with partial pass")
    parser.add_argument("--test-failed", type=int, default=0, help="Skills that failed tests")

    # Security metrics
    parser.add_argument("--sec-clean", type=int, default=0, help="Skills clean (PASS)")
    parser.add_argument("--sec-warned", type=int, default=0, help="Skills with warnings (WARN)")
    parser.add_argument("--sec-blocked", type=int, default=0, help="Skills blocked (BLOCK)")

    # Optimize metrics
    parser.add_argument("--optimized", type=int, default=0, help="Skills optimized")
    parser.add_argument("--unchanged", type=int, default=0, help="Skills reviewed but unchanged")
    parser.add_argument("--changes", type=int, default=0, help="Total changes applied")

    # Publish metrics
    parser.add_argument("--published", type=int, default=0, help="Skills published to GitHub")
    parser.add_argument("--repos-created", type=int, default=0, help="New repos created")
    parser.add_argument("--readmes", type=int, default=0, help="READMEs generated")
    parser.add_argument("--logos", type=int, default=0, help="Logos generated")

    # Catalog metrics
    parser.add_argument("--total-skills", type=int, default=0, help="Total skills in catalog")
    parser.add_argument("--total-edges", type=int, default=0, help="Total relationship edges")

    # Status
    parser.add_argument("--skipped-phases", default="", help="Comma-separated phases skipped")
    parser.add_argument("--errors", default="", help="phase:message pairs, comma-separated")

    # Output
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")

    args = parser.parse_args()
    report = build_report(args)

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Report written to: {output_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
