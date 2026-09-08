# Project Memory

Project Memory is a reusable coding-agent skill for durable, token-efficient project continuity.

Instead of storing every implementation update in one ever-growing Markdown file, it uses a small summary plus topic-specific records:

```text
.agents/MEMORY/
├── SUMMARY.md
└── records/
    ├── architecture/
    ├── decisions/
    ├── features/
    ├── incidents/
    └── migrations/
```

Agents always read `SUMMARY.md` and load only the records relevant to their current task.

## Why

A single implementation-status document eventually becomes expensive to read, difficult to maintain, and full of stale chronology. Project Memory keeps current state concise while preserving durable detail in targeted records.

## Install

Clone this repository into a project's skill directory:

```bash
git clone https://github.com/pedroantonnio/project-memory.git .agents/SKILLS/project-memory
```

Then require agents to read:

```text
.agents/SKILLS/project-memory/SKILL.md
```

before implementation.

## Quick start

```bash
python .agents/SKILLS/project-memory/scripts/memory.py --repo . init
python .agents/SKILLS/project-memory/scripts/memory.py --repo . status
python .agents/SKILLS/project-memory/scripts/memory.py --repo . create --type feature --slug finances --title "Finances"
python .agents/SKILLS/project-memory/scripts/memory.py --repo . validate
```

## Principles

- Summary is small and current.
- Records hold durable detail.
- Only relevant records are loaded.
- Significant project knowledge is versioned with the code.
- Temporary task coordination stays in the coordination system, not Project Memory.
- No secrets or private chain-of-thought are stored.

See `SKILL.md` for the full protocol.
