# skill-lifecycle — Lessons Learned

### 2026-02-14 — Pipeline missing skill-tester phase
- **Friction**: Lifecycle SKILL.md had 5 phases (Audit → Optimize → Publish → Catalog → Report)
  but was missing skill-tester between Audit and Optimize. skill-tester's own SKILL.md
  (line 141) correctly documented the 6-phase pipeline but lifecycle didn't match.
- **Fix**: Added Phase 2 (Test) to lifecycle. Updated all phase numbers, prerequisites,
  error handling dependency table, retry guidance, and run single phase section.
- **Rule**: When adding a new sub-skill to a pipeline, update ALL references in the
  orchestrator skill — not just the overview table. Grep for phase numbers, dependency
  rules, quick reference sections, and prerequisites.

### 2026-02-14 — Executor skipping documented phases
- **Friction**: When executing lifecycle, jumped straight to Publish without running
  Audit, Test, or Optimize. User had to explicitly call out each missing phase.
- **Fix**: Always follow the SKILL.md pipeline sequentially. Read the full workflow
  before starting execution, not just the phase relevant to the user's words.
- **Rule**: A pipeline skill means ALL phases run in order. The user invoking
  `/skill-lifecycle` means the FULL pipeline, not cherry-picking phases.
  If skipping is appropriate, present the plan first and let the user decide.

### 2026-09-25 — Frozen sub-skills, a retired skill-graph, and a report that marks notes as failures
- **Friction**: curator/optimizer/publisher all carry `disable-model-invocation: true`, so the "delegate via Task tool: use /skill-X" pattern cannot work — subagents cannot invoke them. `skill-graph` was archived 2026-08-26 but Phase 4 still calls its scan_skills.py. `lifecycle_report.py` reports a Security phase this SKILL.md does not have (0/0/0 shown as OK unless skipped), and `--errors` marks a phase FAILED and drops its metrics. `publish.py` skips the push at an empty `Proceed? [y/N]` and still exits 0.
- **Fix**: ran each sub-skill from the main thread by reading its SKILL.md; panels went to general-purpose agents with self-contained prompts. Phase 4 used `~/.claude/skills-archive/skill-graph-20260826/scripts/scan_skills.py`. Report regenerated with `--skipped-phases security` and no `--errors`; notes appended by hand. Push confirmed with `printf 'y\n' |` and checked by `git fetch` + `status -sb`.
- **Rule**: before a run, check sub-skill flags and every script path in Phase 0; confirm each push against the remote, not publish.py's exit code.
