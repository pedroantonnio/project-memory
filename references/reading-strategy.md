# Reading strategy

Project Memory is designed to reduce context cost.

## Default retrieval sequence

1. Read `.agents/MEMORY/SUMMARY.md`.
2. Identify the task's domains and technologies.
3. Follow only summary links whose `Read when` guidance matches the task.
4. If context is still missing, use `memory.py search` or `memory.py context`.
5. Read the smallest set of records that resolves the uncertainty.
6. Inspect current code/tests/configuration before acting on implementation details.

## Do not preload everything

Do not recursively read all records as a startup ritual.

The store may eventually contain years of architecture, feature, incident, and migration context. Loading it all defeats the design.

## Search examples

```bash
python <skill-root>/scripts/memory.py --repo <repo> search --query "r2 cors upload"
python <skill-root>/scripts/memory.py --repo <repo> context --query "finance forecast revenue" --max-records 5
```

## When summary is enough

If the task only needs a high-level invariant already stated in `SUMMARY.md`, do not load the detailed record unless the implementation decision depends on it.

## When to expand

Open a record when:

- the summary explicitly says to read it for the current type of task;
- the task changes that area;
- you need rationale behind a durable decision;
- current code appears inconsistent with memory;
- you are resolving a cross-area conflict;
- you need incident history to avoid reintroducing a known failure.

## Stale memory

If a record conflicts with current code/runtime evidence, do not blindly obey either source. Determine whether:

- the code is mid-migration;
- the memory is stale;
- the current task is intentionally changing the contract;
- project-specific normative documentation resolves the conflict.

Correct stale memory when the truth is verified and the correction is relevant to the task.
