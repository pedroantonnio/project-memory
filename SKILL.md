---
name: project-memory
description: Durable, token-efficient project memory for coding agents. Maintains a compact project summary plus linked Markdown records for architecture, decisions, features, incidents, and migrations, so agents load only relevant context and update durable knowledge without relying on a single ever-growing implementation log.
---

# Project Memory

A durable, token-efficient project memory protocol for coding agents.

## Purpose

Project Memory preserves durable engineering context without forcing every agent to reread an ever-growing implementation log.

The memory store is versioned with the project and lives at:

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

`SUMMARY.md` is the small routing layer. Detailed context lives in topic-specific records and is loaded only when relevant.

This skill manages durable project knowledge. It does not replace task coordination, Git worktree isolation, tests, code review, or the Cooperative Worktree Agents ledger.

## Mandatory operating model

When this skill is required by `AGENTS.md`, use it for every development task.

1. Work from the task/worktree required by the repository's coordination workflow.
2. Locate the repository root for the task you are actually implementing.
3. Ensure `.agents/MEMORY/` exists. If it does not, initialize it with this skill.
4. Read `.agents/MEMORY/SUMMARY.md` before implementation.
5. Open only the records relevant to the current task.
6. Treat Project Memory as durable context, not as a substitute for inspecting current code, tests, schemas, or runtime behavior.
7. During implementation, record only durable facts that will matter to future agents.
8. Before declaring the task ready for integration, update affected records and `SUMMARY.md` if the summarized current state changed.
9. Validate the memory store.
10. Commit memory changes with the task that caused them.

Do not maintain a single append-only implementation log.

## Relationship to Cooperative Worktree Agents

The two systems have different responsibilities:

```text
Cooperative Worktree Agents
= execution coordination
= task ownership
= branches/worktrees
= claims
= validation/integration
= handoff/cleanup

Project Memory
= durable project knowledge
= current architecture
= durable decisions
= current feature state
= significant incidents
= long-running migrations
```

The CWA ledger under the Git common directory is operational and task-oriented. `.agents/MEMORY/` is versioned project knowledge.

Do not copy CWA journals, lock state, agent status, temporary task notes, or private scratch reasoning into Project Memory.

## Read strategy

Always read:

```text
.agents/MEMORY/SUMMARY.md
```

Then read only records whose scope or `Read when` guidance is relevant to the task.

Examples:

- Upload/CORS task: read storage architecture and relevant upload incident records.
- Finance task: read finance feature records and any finance-specific decisions.
- Authentication task: do not load Selection, Delivery, or Finance records unless they are actually relevant.

Do not recursively read every record "just in case".

If `SUMMARY.md` links to ten areas and only two matter, load those two.

See `references/reading-strategy.md`.

## Memory hierarchy

Project Memory is a navigation and continuity layer. When memory conflicts with current observable reality, investigate before proceeding.

Use this evidence order when resolving stale memory:

1. explicit current user requirements;
2. current code, schema, tests, configuration, and runtime evidence;
3. current project-specific normative documentation;
4. Project Memory;
5. historical records.

If Project Memory is stale, fix it in the same task when the correction is durable and relevant.

Never silently preserve a known-false statement just because it already exists in memory.

## Memory structure

### `SUMMARY.md`

`SUMMARY.md` represents the current project state at a high level and routes agents to detailed records.

It must:

- remain small;
- describe current state, not a complete chronology;
- avoid long implementation narratives;
- link to detailed records;
- say when a linked record should be read;
- remove or rewrite stale summaries when reality changes.

Targets:

- ideal: <= 200 lines;
- ideal: <= 12 KiB UTF-8;
- no hard chronological append section that grows forever.

If a summary section becomes detailed, move the details into a record and reduce the summary to a few current-state lines plus a link.

### `records/architecture/`

Use for durable system structure and invariants.

Examples:

- persistence architecture;
- storage topology;
- authentication architecture;
- queue/background-processing architecture.

### `records/decisions/`

Use for durable decisions where future agents need to know both the decision and why it exists.

Examples:

- shared Resource Detail architecture;
- canonical identifier strategy;
- chosen API boundary.

Do not create decision records for trivial implementation choices.

### `records/features/`

Use for the current consolidated state of important product/engineering areas.

Feature records are living documents. Update the existing feature record when its current state changes instead of creating a new dated record for every task.

Examples:

- `selection.md`;
- `delivery.md`;
- `finances.md`.

### `records/incidents/`

Use for significant failures whose cause, fix, or prevention is likely to matter again.

Incident records are historical and should normally remain after resolution.

Examples:

- cross-origin direct-upload failure;
- data-loss prevention incident;
- critical cache invalidation bug.

Do not record every ordinary bug.

### `records/migrations/`

Use for long-running transitions that span multiple tasks or releases.

Examples:

- database migration;
- auth-provider migration;
- storage migration.

A migration record should emphasize current phase, verified gates, blockers, rollback constraints, and completion criteria rather than becoming a raw command transcript.

## Record format

Every record must begin with frontmatter:

```yaml
---
id: r2-storage
type: architecture
status: active
created: 2026-09-08
updated: 2026-09-08
scope:
  - storage
  - uploads
  - r2
---
```

Required fields:

- `id`: stable lowercase kebab-case identifier;
- `type`: `architecture`, `decision`, `feature`, `incident`, or `migration`;
- `status`: normally `active`, `resolved`, `superseded`, `completed`, or `archived` as appropriate;
- `created`: ISO date;
- `updated`: ISO date;
- `scope`: one or more search terms representing the record's area.

Recommended body sections:

```markdown
# Title

## Current state

## Read when

## Decisions and invariants

## Important implementation details

## Related files

## Related records

## Relevant commits
```

Adapt sections to the record type. Do not add empty sections mechanically.

See `references/record-format.md`.

## What belongs in memory

Write memory when a task changes or establishes something that is likely to matter to future work, including:

- architecture;
- public/internal contracts used across areas;
- durable business invariants;
- important feature state;
- non-obvious security constraints;
- infrastructure topology;
- significant incident cause/fix/prevention;
- long-running migration state;
- important compatibility constraints;
- decisions future agents might otherwise repeatedly rediscover.

## What does not belong in memory

Do not write memory for:

- formatting-only changes;
- minor spacing or visual tweaks;
- variable renames;
- one-off debugging output;
- temporary task state;
- raw terminal transcripts;
- test output already available in CI/task evidence;
- implementation details obvious from nearby code and unlikely to affect future decisions;
- speculative future ideas that the user explicitly said not to implement or preserve as project state;
- secrets, tokens, passwords, credentials, private keys, presigned URLs, or sensitive user data;
- hidden chain-of-thought or private scratch reasoning.

## Updating `SUMMARY.md`

Update the summary only when the summarized current state changes.

A good summary entry contains:

1. area name;
2. one to three current-state statements;
3. `Read when` guidance;
4. relative link to the detailed record.

Example:

```markdown
### R2 storage

Private binary assets use Cloudflare R2 with browser direct uploads where supported.

Read when working on storage, upload, download, CORS, presigned URLs, or asset processing.

→ [R2 storage](records/architecture/r2-storage.md)
```

Do not duplicate the record body in `SUMMARY.md`.

## Superseding memory

When a durable decision is replaced:

- create or update the new active record;
- mark the old decision `superseded`;
- link old and new records to each other;
- update `SUMMARY.md` to point to current reality;
- do not delete useful historical rationale unless it is unsafe or incorrect to retain.

When a feature record changes, update the living feature record rather than preserving obsolete current-state prose.

## Record naming

Use predictable lowercase kebab-case filenames.

Recommended patterns:

```text
architecture/r2-storage.md
features/selection.md
features/finances.md
decisions/2026-09-08-shared-resource-detail.md
incidents/2026-09-08-r2-upload-cors.md
migrations/d1-to-supabase.md
```

Use dates for historical event-like records such as decisions and incidents when useful. Do not date living feature/architecture records unless there is a specific reason.

## Tooling

This skill includes a standard-library Python helper:

```text
scripts/memory.py
```

Use the helper from the skill installation, pointing it at the project/task repository with `--repo`.

Examples:

```bash
python <skill-root>/scripts/memory.py --repo <repo> init
python <skill-root>/scripts/memory.py --repo <repo> status
python <skill-root>/scripts/memory.py --repo <repo> validate
python <skill-root>/scripts/memory.py --repo <repo> create --type feature --slug finances --title "Finances"
python <skill-root>/scripts/memory.py --repo <repo> search --query "r2 upload cors"
python <skill-root>/scripts/memory.py --repo <repo> context --query "selection delivery files" --max-records 5
```

If the skill directory is absent from a generated worktree because the skill is installed as an untracked/nested repository in the primary checkout, invoke `memory.py` by absolute path from the primary skill installation and set `--repo` to the task worktree.

### `init`

Creates the memory directory structure and starter `SUMMARY.md` without overwriting existing memory files.

### `status`

Reports summary size, record counts, categories, and validation warnings.

### `validate`

Checks:

- required directory structure;
- summary size targets;
- Markdown links from `SUMMARY.md` into `records/`;
- required record frontmatter;
- allowed record types;
- stable ID format;
- date format;
- duplicate IDs;
- type/directory consistency;
- obvious secret-like patterns.

Validation is intentionally conservative. It does not claim semantic truth.

### `create`

Creates a record from the standard template without overwriting an existing path.

### `search`

Searches summary and records by words in title, metadata, and body. Use it to locate relevant context without loading the entire memory tree.

### `context`

Ranks records for a query and prints a compact retrieval plan: summary plus the most relevant record paths. It is a routing helper, not a semantic embedding system.

## Required validation before task completion

If `.agents/MEMORY/` exists, run:

```bash
python <skill-root>/scripts/memory.py --repo <task-worktree> validate
```

before reporting the task ready/complete.

If memory files changed, also review:

```text
.agents/MEMORY/SUMMARY.md
```

for stale statements, duplicated detail, and unnecessary growth.

A successful validator does not prove the memory content is factually correct. The agent is responsible for factual review.

## Concurrency

Project Memory files are ordinary versioned project files. Multiple task worktrees may edit them concurrently.

Therefore:

- keep changes scoped;
- prefer one feature/record file over broad rewrites;
- avoid reformatting unrelated memory files;
- expect normal Git conflicts in `SUMMARY.md` when concurrent tasks change current state;
- resolve memory conflicts semantically so compatible knowledge from both tasks survives;
- use the repository's cooperative integration workflow for conflict handling.

Do not introduce a second lock system inside Project Memory.

## Initialization behavior

If `.agents/MEMORY/` does not exist, initialize it rather than recreating an `implementation_status.md`-style monolith.

The initial structure is:

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

Do not populate records with guessed project facts. Start with an honest minimal summary and add records only from verified context.

## Maintenance rule

The memory system is healthy when:

- `SUMMARY.md` remains quick to read;
- agents can identify relevant records without scanning everything;
- active records describe current reality;
- historical records preserve only useful durable context;
- significant changes update memory as part of the same task;
- stale or superseded information is clearly marked;
- secrets and private reasoning never enter the store.

See `references/maintenance.md`.
