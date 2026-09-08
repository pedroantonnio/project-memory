# Maintenance

## Keep the summary bounded

`SUMMARY.md` is a routing index and current-state overview.

Targets:

- <= 200 lines;
- <= 12 KiB UTF-8;
- no append-only release history;
- no copied incident reports;
- no duplicated record bodies.

When it grows, extract details into records and shorten the summary.

## Prefer living records for current state

Feature and architecture records should normally be updated in place.

Do not create:

```text
features/selection-v1.md
features/selection-v2.md
features/selection-final.md
features/selection-final-2.md
```

Keep one current record and use decision/incident/history records where historical rationale matters.

## Preserve useful history selectively

Decision and incident records can remain after they stop being current because their rationale or prevention value may matter later.

Mark them `superseded`, `resolved`, or `archived` as appropriate.

## Avoid memory spam

A task should not update Project Memory merely because files changed.

Write memory only when future agents are likely to benefit.

Examples that usually do not merit memory:

- button padding;
- copy edits;
- formatting;
- local variable names;
- ordinary dependency bumps without architectural consequences;
- temporary debugging steps.

## Validate links and metadata

Run:

```bash
python <skill-root>/scripts/memory.py --repo <repo> validate
```

before task completion when the project has a memory store.

## Review stale summary entries

When touching an area, check whether its summary entry still represents current reality. Remove resolved blockers and obsolete statements.

## Security

Never store:

- passwords;
- access tokens;
- API secrets;
- private keys;
- session cookies;
- presigned URLs;
- sensitive personal data;
- hidden chain-of-thought.

Record safe identifiers, architecture, and redacted operational context only when needed.
