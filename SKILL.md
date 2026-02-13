---
name: skill-lifecycle
description: >-
  This skill should be used when the user asks to "run skill maintenance",
  "skill lifecycle", "maintain skills", "skill 維護", "skill 生命週期",
  "定期整理 skill", mentions skill maintenance automation, or discusses
  running the full skill curation → optimization → publishing → catalog pipeline.
version: 0.1.0
tools: Task, Read, Write, Glob, Bash
---

# Skill Lifecycle

Orchestrate the full skill maintenance pipeline: audit inventory for redundancies,
optimize flagged skills, publish updates to GitHub, and regenerate the catalog with
interactive graph visualization. Each phase delegates to a specialized sub-skill via
the Task tool, running sequentially with user checkpoints.

## Pipeline Overview

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐     ┌────────┐
│  Audit  │ ──► │ Optimize │ ──► │ Publish │ ──► │ Catalog │ ──► │ Report │
│ curator │     │ optimizer│     │publisher│     │ catalog │     │ summary│
└─────────┘     └──────────┘     └─────────┘     └─────────┘     └────────┘
      │               │
      ▼               │
 [User checkpoint:    │
  approve/skip]  ◄────┘
```

**Phases map to sub-skills:**

| Phase | Sub-Skill | What It Does |
|-------|-----------|--------------|
| Audit | `skill-curator` | Scan for overlaps, run 3-agent panel, recommend merges/splits |
| Optimize | `skill-optimizer` | Review flagged skills, gather evidence, apply targeted updates |
| Publish | `skill-publisher` | Push to GitHub, generate READMEs, create logos |
| Catalog | `skill-catalog` | Extract metadata, build relationship graph, generate HTML viewer |
| Report | (built-in) | Summarize all changes across the pipeline |

## Prerequisites

All four sub-skills must be installed:

```bash
ls ~/.claude/skills/skill-curator/SKILL.md \
   ~/.claude/skills/skill-optimizer/SKILL.md \
   ~/.claude/skills/skill-publisher/SKILL.md \
   ~/.claude/skills/skill-catalog/SKILL.md
```

If any are missing, inform the user and skip that phase (do not fail the entire pipeline).

## Workflow

### Phase 0: Initialize

1. **Verify sub-skills** — Check that all four sub-skill directories exist
2. **Create run log** — Initialize a tracking structure to record results from each phase:

```
Run ID: lifecycle-YYYYMMDD-HHMMSS
Phases: [audit, optimize, publish, catalog]
Results: {}
Errors: {}
```

3. **Present the plan** — Show the user what will happen:

```markdown
## Skill Lifecycle Run

Pipeline: Audit → Optimize → Publish → Catalog → Report

| Phase | Sub-Skill | Status |
|-------|-----------|--------|
| 1. Audit | skill-curator | Pending |
| 2. Optimize | skill-optimizer | Pending |
| 3. Publish | skill-publisher | Pending |
| 4. Catalog | skill-catalog | Pending |
| 5. Report | lifecycle_report.py | Pending |

Proceed? (y/n, or skip phases with: "skip audit", "skip publish", etc.)
```

Wait for user confirmation. Parse any skip directives.

### Phase 1: Audit (skill-curator)

**Delegate via Task tool** with a sub-agent:

```
Use the /skill-curator skill to perform a full skill inventory audit.

Steps:
1. Run the overlap analysis: python3 ~/.claude/skills/skill-curator/scripts/analyze.py --json
2. For each non-trivial cluster, run the 3-agent panel discussion (Consolidator, Preservationist, Synthesizer)
3. Present the recommendation table

Output format — return a structured summary:
- clusters_found: number of overlap clusters identified
- recommendations: list of {cluster, skills, verdict (MERGE/KEEP/SPLIT/RETIRE), confidence}
- actions_taken: list of {action, source_skills, result_skill} (empty until user approves)
```

**After the audit sub-agent completes:**

1. Present the curator's recommendations to the user
2. **CHECKPOINT — Wait for user approval:**

```markdown
## Audit Results

[Curator's recommendation table here]

### What would you like to do?
- **approve all** — Execute all recommended merges/splits, then continue to Optimize
- **approve N** — Approve specific cluster numbers (e.g., "approve 1, 3")
- **skip** — Skip to Optimize without making changes
- **stop** — End the lifecycle run here
```

3. If approved, let the curator sub-agent execute the approved changes
4. Record results:
   - `skills_merged`: list of merge operations performed
   - `skills_split`: list of split operations performed
   - `skills_retired`: list of retired skills
   - `clusters_skipped`: list of clusters the user declined

### Phase 2: Optimize (skill-optimizer)

Determine which skills need optimization. Candidates come from two sources:

1. **Skills modified in Phase 1** — Newly merged or split skills need a quality check
2. **Skills with observations.md** — Previously deferred findings that may now have enough evidence

Discover candidates:

```bash
# Find skills with pending observations
for skill_dir in ~/.claude/skills/*/; do
  if [ -f "$skill_dir/observations.md" ]; then
    echo "$(basename $skill_dir)"
  fi
done
```

**For each candidate, delegate via Task tool:**

```
Use the /skill-optimizer skill to review and optimize the skill: [skill-name]

Context: This is part of a lifecycle maintenance run.
[If from Phase 1]: This skill was recently [merged from X+Y / split from Z]. Review the
merged content for coherence and quality.
[If from observations]: This skill has pending observations in observations.md. Check if
deferred findings now have enough evidence to act on.

Output format — return:
- skill_name: name
- changes_made: list of {category, title, description}
- version_bump: old_version → new_version (or "no change")
- observations_resolved: number of observations promoted to changes
- observations_remaining: number still deferred
```

**Optimization runs sequentially** — each skill one at a time, because the optimizer
may need to read conversation context from previous optimizations.

Record results:
- `skills_optimized`: list of skills that received changes
- `skills_unchanged`: list of skills reviewed but not changed
- `total_changes`: count of all changes applied

### Phase 3: Publish (skill-publisher)

Publish all skills that were modified in Phases 1 or 2.

**Delegate via Task tool:**

```
Use the /skill-publisher skill to publish the following skills: [list]

For each skill:
1. Generate/update README.md and README.zh-TW.md
2. Generate logo if missing (use /image-gen)
3. Push to GitHub under joneshong-skills org
4. Trigger DeepWiki indexing

Use --scan first to show current publish status, then process only the modified skills.

Output format — return:
- skills_published: list of {name, repo_url, readme_generated, logo_generated}
- skills_failed: list of {name, error}
- deepwiki_indexed: list of skill names
```

If no skills were modified in earlier phases, skip this phase and note it in the report.

Record results:
- `repos_created`: count of new GitHub repos
- `repos_updated`: count of existing repos pushed
- `readmes_generated`: count
- `logos_generated`: count
- `publish_failures`: list of any failures

### Phase 4: Catalog (skill-catalog)

Regenerate the full catalog and interactive graph to reflect all changes.

**Delegate via Task tool:**

```
Use the /skill-catalog skill to regenerate the full skill catalog and graph.

Steps:
1. Run: python3 ~/.claude/skills/skill-catalog/scripts/extract_catalog.py -o ~/Downloads/skill-catalog.json
2. Run: python3 ~/.claude/skills/skill-graph/scripts/scan_skills.py --json -o ~/Downloads/skill-graph.json
3. Run: python3 ~/.claude/skills/skill-catalog/scripts/generate_viewer.py \
     --graph ~/Downloads/skill-graph.json \
     --catalog ~/Downloads/skill-catalog.json \
     -o ~/Downloads/skill-graph-viewer.html
4. Open the viewer: open ~/Downloads/skill-graph-viewer.html

Output format — return:
- total_skills: number
- total_edges: number
- catalog_path: file path
- graph_path: file path
- viewer_path: file path
```

Record results:
- `total_skills`: final skill count
- `total_edges`: relationship count
- `catalog_path`: path to JSON export
- `viewer_path`: path to HTML viewer

### Phase 5: Report

Generate the final lifecycle report summarizing all phases.

```bash
python3 ~/.claude/skills/skill-lifecycle/scripts/lifecycle_report.py \
  --run-id "lifecycle-YYYYMMDD-HHMMSS" \
  --audit-merges N --audit-splits N --audit-retires N \
  --optimized N --unchanged N --changes N \
  --published N --repos-created N --readmes N --logos N \
  --total-skills N --total-edges N \
  --skipped-phases "phase1,phase2" \
  --errors "phase:message,phase:message" \
  -o ~/Downloads/lifecycle-report-YYYYMMDD.md
```

Present the report to the user and provide the file path.

## Error Handling

Each phase is wrapped in error recovery logic. If a phase fails:

1. **Capture the error** — Record the phase name, error message, and partial results
2. **Do not abort** — Continue to the next phase unless it depends on the failed phase
3. **Report at the end** — Include all errors in the final report

### Phase Dependency Rules

| If This Fails... | Then... |
|-------------------|---------|
| Audit | Optimize still runs (uses observations.md as candidates instead) |
| Optimize | Publish still runs (publishes whatever was changed in Audit) |
| Publish | Catalog still runs (catalog reflects local state, not GitHub state) |
| Catalog | Report still runs (reports on earlier phases without catalog stats) |

### Retry Guidance

The report includes a retry section for any failed phases:

```markdown
## Retry Failed Phases

To retry failed phases individually:
- Audit: `/skill-curator`
- Optimize: `/skill-optimizer [skill-name]`
- Publish: `/skill-publisher --all`
- Catalog: `/skill-catalog`
```

## Quick Reference

### Run Full Pipeline

```
/skill-lifecycle
```

or: "run skill maintenance", "skill 維護", "定期整理 skill"

### Skip Specific Phases

At the Phase 0 prompt, say:
- "skip audit" — Jump to Optimize
- "skip publish" — Skip GitHub push, go straight to Catalog
- "skip audit, publish" — Only run Optimize + Catalog

### Run Single Phase

For individual phases, use the sub-skill directly:
- Audit only: `/skill-curator`
- Optimize only: `/skill-optimizer`
- Publish only: `/skill-publisher --all`
- Catalog only: `/skill-catalog`

### Recommended Cadence

| Frequency | What to Run |
|-----------|-------------|
| After building 3+ new skills | Full pipeline |
| After major skill edits | Optimize → Publish → Catalog |
| Weekly (if actively building) | Full pipeline |
| Monthly (maintenance mode) | Full pipeline |

## Continuous Improvement

This skill evolves with each use. After every invocation:

1. **Reflect** — Identify what worked, what caused friction, and any unexpected issues
2. **Record** — Append a concise lesson to `lessons.md` in this skill's directory
3. **Refine** — When a pattern recurs (2+ times), update SKILL.md directly

### lessons.md Entry Format

```
### YYYY-MM-DD — Brief title
- **Friction**: What went wrong or was suboptimal
- **Fix**: How it was resolved
- **Rule**: Generalizable takeaway for future invocations
```

Accumulated lessons signal when to run `/skill-optimizer` for a deeper structural review.

## Additional Resources

### Scripts
- **`scripts/lifecycle_report.py`** — Generate markdown summary report from pipeline results.
  Usage: `python3 lifecycle_report.py --run-id ID [phase flags] [-o OUTPUT]`
