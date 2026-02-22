[English](README.md) | [繁體中文](README.zh.md)

# skill-lifecycle

Orchestrate the full skill maintenance pipeline: audit, optimize, publish, and catalog.

## 說明

Skill Lifecycle runs the complete skill maintenance workflow in sequence — curator → optimizer → publisher → catalog — with user checkpoints between phases and progress reporting throughout.

## 功能特色

- Orchestrates 4-phase skill maintenance pipeline
- Phase 1: Skill Curator — identify and resolve redundancies
- Phase 2: Skill Optimizer — refine and improve flagged skills
- Phase 3: Skill Publisher — push updates to GitHub
- Phase 4: Skill Catalog — regenerate the inventory with graph
- User checkpoint after each phase before proceeding

## 使用方式

透過以下觸發語句呼叫 Claude Code 來使用此技能：

- "run skill maintenance"
- "skill lifecycle"
- "maintain skills"
- "skill 維護"
- "定期整理 skill"

## 相關技能

- [`skill-curator`](https://github.com/joneshong-skills/skill-curator)
- [`skill-optimizer`](https://github.com/joneshong-skills/skill-optimizer)
- [`skill-publisher`](https://github.com/joneshong-skills/skill-publisher)
- [`skill-catalog`](https://github.com/joneshong-skills/skill-catalog)

## 安裝

將技能目錄複製到 Claude Code 技能資料夾：

```
cp -r skill-lifecycle ~/.claude/skills/
```

放置在 `~/.claude/skills/` 的技能會被 Claude Code 自動發現，無需額外註冊。
