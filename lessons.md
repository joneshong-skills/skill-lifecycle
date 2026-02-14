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
