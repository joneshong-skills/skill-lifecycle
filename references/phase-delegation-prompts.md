# Phase Delegation Prompts

Detailed Task tool prompt templates for each lifecycle phase.

## Phase 1: Audit (skill-curator)

```
Use the /skill-curator skill to perform a full skill inventory audit.

Steps:
1. Run the overlap analysis: ~/.local/bin/python3 ~/.claude/skills/skill-curator/scripts/analyze.py --json
2. For each non-trivial cluster, run the 3-agent panel discussion (Consolidator, Preservationist, Synthesizer)
3. Present the recommendation table

Output format — return a structured summary:
- clusters_found: number of overlap clusters identified
- recommendations: list of {cluster, skills, verdict (MERGE/KEEP/SPLIT/RETIRE), confidence}
- actions_taken: list of {action, source_skills, result_skill} (empty until user approves)
```

After audit completes, present recommendations with checkpoint options:

```markdown
## Audit Results

[Curator's recommendation table here]

### What would you like to do?
- **approve all** — Execute all recommended merges/splits, then continue to Optimize
- **approve N** — Approve specific cluster numbers (e.g., "approve 1, 3")
- **skip** — Skip to Optimize without making changes
- **stop** — End the lifecycle run here
```

Record: `skills_merged`, `skills_split`, `skills_retired`, `clusters_skipped`.

## Phase 2: Test (skill-tester)

```
Use the /skill-tester skill to validate the following skills: [list]

Steps:
1. Run: ~/.local/bin/python3 ~/.claude/skills/skill-tester/scripts/scan_env.py
2. For each skill, run T1–T4 automated checks (dependency, syntax, consistency, runtime)
3. Dispatch T5 scenario tests in parallel batches of 6
4. Aggregate results with gen_report.py

Output format — return:
- total_tested: number
- passed: list of skill names
- partial: list of {name, issues}
- failed: list of {name, issues}
```

Skills with FAIL become candidates for Phase 4 (Optimize). Auto-fixable issues (missing deps, stale refs) can be fixed immediately.

Record: `skills_passed`, `skills_partial`, `skills_failed`, `auto_fixed`.

## Phase 3: Security (skill-security-scan)

```bash
~/.local/bin/python3 ~/.claude/skills/skill-security-scan/scripts/security-scan.py --batch --json
```

| Result | Action |
|--------|--------|
| `PASS` | Skill proceeds to next phase |
| `WARN` | Skill proceeds but warning logged in report |
| `BLOCK` | Skill **removed from pipeline** — must be fixed manually first |

BLOCKED skills do NOT proceed to Optimize or Publish.

Record: `skills_clean`, `skills_warned`, `skills_blocked`.

## Phase 4: Optimize (skill-optimizer)

Candidate discovery:

```bash
# Find skills with pending observations
for skill_dir in ~/.claude/skills/*/; do
  if [ -f "$skill_dir/observations.md" ]; then
    echo "$(basename $skill_dir)"
  fi
done
```

Delegation per candidate:

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

Runs **sequentially** — each skill one at a time.

Record: `skills_optimized`, `skills_unchanged`, `total_changes`.

## Phase 5: Publish (skill-publisher)

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

Record: `repos_created`, `repos_updated`, `readmes_generated`, `logos_generated`, `publish_failures`.

## Phase 6: Catalog (skill-catalog + skill-graph)

```
Use the /skill-catalog skill to regenerate the full skill catalog and graph.

Steps:
1. Run: ~/.local/bin/python3 ~/.claude/skills/skill-catalog/scripts/extract_catalog.py -o ~/Downloads/skill-catalog.json
2. Run: ~/.local/bin/python3 ~/.claude/skills/skill-graph/scripts/scan_skills.py --json -o ~/Downloads/skill-graph.json
3. Run: ~/.local/bin/python3 ~/.claude/skills/skill-catalog/scripts/generate_viewer.py \
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

Record: `total_skills`, `total_edges`, `catalog_path`, `viewer_path`.

## Phase 7: Report

Preferred (Sandbox):
```python
import os, sys; sys.path.insert(0, os.path.expanduser('~/.claude/skills/skill-lifecycle/scripts'))
import lifecycle_report
report = lifecycle_report.generate(run_id='lifecycle-YYYYMMDD-HHMMSS', **phase_results)
output(report)
```

Fallback (Bash):
```bash
~/.local/bin/python3 ~/.claude/skills/skill-lifecycle/scripts/lifecycle_report.py \
  --run-id "lifecycle-YYYYMMDD-HHMMSS" \
  --audit-merges N --audit-splits N --audit-retires N \
  --tested N --test-passed N --test-partial N --test-failed N \
  --sec-clean N --sec-warned N --sec-blocked N \
  --optimized N --unchanged N --changes N \
  --published N --repos-created N --readmes N --logos N \
  --total-skills N --total-edges N \
  --skipped-phases "phase1,phase2" \
  --errors "phase:message,phase:message" \
  -o ~/workshop/outputs/skill-lifecycle/report.md
```
