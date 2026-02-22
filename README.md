[English](README.md) | [繁體中文](README.zh.md)

# skill-lifecycle

Orchestrate the full skill maintenance pipeline: audit, optimize, publish, and catalog.

## Description

Skill Lifecycle runs the complete skill maintenance workflow in sequence — curator → optimizer → publisher → catalog — with user checkpoints between phases and progress reporting throughout.

## Features

- Orchestrates 4-phase skill maintenance pipeline
- Phase 1: Skill Curator — identify and resolve redundancies
- Phase 2: Skill Optimizer — refine and improve flagged skills
- Phase 3: Skill Publisher — push updates to GitHub
- Phase 4: Skill Catalog — regenerate the inventory with graph
- User checkpoint after each phase before proceeding

## Usage

Invoke by asking Claude Code with trigger phrases such as:

- "run skill maintenance"
- "skill lifecycle"
- "maintain skills"
- "skill 維護"
- "定期整理 skill"

## Related Skills

- [`skill-curator`](https://github.com/joneshong-skills/skill-curator)
- [`skill-optimizer`](https://github.com/joneshong-skills/skill-optimizer)
- [`skill-publisher`](https://github.com/joneshong-skills/skill-publisher)
- [`skill-catalog`](https://github.com/joneshong-skills/skill-catalog)

## Install

Copy the skill directory into your Claude Code skills folder:

```
cp -r skill-lifecycle ~/.claude/skills/
```

Skills placed in `~/.claude/skills/` are auto-discovered by Claude Code. No additional registration is needed.
