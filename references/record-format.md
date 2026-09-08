# Record format

Every record uses UTF-8 Markdown with YAML-style frontmatter.

## Required metadata

```yaml
---
id: selection
type: feature
status: active
created: 2026-09-08
updated: 2026-09-08
scope:
  - selection
  - files
  - client-review
---
```

### `id`

Stable lowercase kebab-case identifier. Do not change it merely because the title changes.

### `type`

Allowed values:

- `architecture`
- `decision`
- `feature`
- `incident`
- `migration`

The record should live in the matching directory.

### `status`

Use a short truthful lifecycle state. Common values:

- `active`
- `resolved`
- `superseded`
- `completed`
- `archived`

### `created` and `updated`

Use ISO `YYYY-MM-DD` dates.

Update `updated` only when the record's durable content changes.

### `scope`

Use concise terms agents can search for. Include domain names, feature names, major technologies, or contracts that make the record discoverable.

## Body guidance

Use only sections that add value. Common sections:

```markdown
# Selection

## Current state

What is true now.

## Read when

Tasks for which this record is relevant.

## Decisions and invariants

Rules that must survive refactors.

## Important implementation details

Non-obvious details that future agents would otherwise rediscover.

## Related files

Paths only when they materially help navigation.

## Related records

Relative Markdown links.

## Relevant commits

Only commits worth preserving as engineering context.
```

## Record-specific guidance

### Architecture

Emphasize topology, boundaries, ownership, invariants, and dependencies.

### Decision

Include:

- context;
- decision;
- rationale;
- consequences;
- supersession links when applicable.

Do not turn decisions into meeting transcripts.

### Feature

Describe current behavior and important contracts. Feature records are living state, not release notes.

### Incident

Include:

- impact;
- symptoms;
- root cause;
- fix;
- prevention/guardrails;
- verification evidence at a useful summary level.

Do not copy raw logs unless a tiny excerpt is essential.

### Migration

Include:

- source and target states;
- current phase;
- verified gates;
- blockers;
- rollback constraints;
- completion criteria.

Avoid endless chronological command logs.
