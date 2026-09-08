#!/usr/bin/env python3
"""Project Memory helper.

Standard-library-only utility for initializing, validating, searching, and
creating a token-efficient `.agents/MEMORY` store.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

CATEGORIES = ("architecture", "decisions", "features", "incidents", "migrations")
TYPE_TO_DIR = {
    "architecture": "architecture",
    "decision": "decisions",
    "feature": "features",
    "incident": "incidents",
    "migration": "migrations",
}
ALLOWED_TYPES = tuple(TYPE_TO_DIR)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)\s*[:=]\s*[^\s<>{}]+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)X-Amz-Signature=[0-9a-f]{32,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]

SUMMARY_TEMPLATE = """# Project Memory Summary

This file is the compact current-state index for the project.

Read this file first. Open linked records only when they are relevant to the current task.

## Current architecture

No architecture records have been added yet.

## Current product / engineering areas

No feature records have been added yet.

## Active migrations

None recorded.

## Active significant incidents

None recorded.

## Important active decisions

None recorded.
"""


@dataclass
class Record:
    path: Path
    metadata: dict[str, object]
    body: str
    text: str


def repo_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository path does not exist or is not a directory: {root}")
    return root


def memory_root(repo: Path) -> Path:
    return repo / ".agents" / "MEMORY"


def records_root(repo: Path) -> Path:
    return memory_root(repo) / "records"


def ensure_structure(repo: Path) -> None:
    root = memory_root(repo)
    (root / "records").mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES:
        (root / "records" / category).mkdir(parents=True, exist_ok=True)
    summary = root / "SUMMARY.md"
    if not summary.exists():
        summary.write_text(SUMMARY_TEMPLATE, encoding="utf-8", newline="\n")


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, text

    meta_lines = lines[1:end]
    body = "\n".join(lines[end + 1 :])
    meta: dict[str, object] = {}
    current_list_key: str | None = None

    for raw in meta_lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        list_match = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if list_match and current_list_key:
            value = list_match.group(1).strip().strip('"\'')
            bucket = meta.setdefault(current_list_key, [])
            if isinstance(bucket, list):
                bucket.append(value)
            continue
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if not kv:
            current_list_key = None
            continue
        key, value = kv.group(1), kv.group(2)
        if value == "":
            meta[key] = []
            current_list_key = key
        else:
            meta[key] = value.strip().strip('"\'')
            current_list_key = None

    return meta, body


def iter_record_paths(repo: Path) -> Iterable[Path]:
    root = records_root(repo)
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def load_records(repo: Path) -> list[Record]:
    result = []
    for path in iter_record_paths(repo):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        result.append(Record(path=path, metadata=meta, body=body, text=text))
    return result


def rel(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def command_init(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    before = memory_root(repo).exists()
    ensure_structure(repo)
    print(f"memory_root={rel(memory_root(repo), repo)}")
    print("status=existing" if before else "status=initialized")
    return 0


def validate(repo: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = memory_root(repo)
    summary = root / "SUMMARY.md"

    if not root.exists():
        errors.append("Missing .agents/MEMORY directory. Run init.")
        return errors, warnings
    if not summary.exists():
        errors.append("Missing .agents/MEMORY/SUMMARY.md.")
    for category in CATEGORIES:
        path = root / "records" / category
        if not path.exists():
            errors.append(f"Missing record category directory: {rel(path, repo)}")

    if summary.exists():
        data = summary.read_bytes()
        text = data.decode("utf-8")
        line_count = len(text.splitlines())
        if line_count > 200:
            warnings.append(f"SUMMARY.md has {line_count} lines; target is <= 200.")
        if len(data) > 12 * 1024:
            warnings.append(f"SUMMARY.md is {len(data)} bytes; target is <= 12288 bytes.")
        for target in MARKDOWN_LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            linked = (summary.parent / clean).resolve()
            try:
                linked.relative_to(root.resolve())
            except ValueError:
                warnings.append(f"SUMMARY.md link points outside memory root: {target}")
                continue
            if not linked.exists():
                errors.append(f"Broken SUMMARY.md link: {target}")

    ids: dict[str, Path] = {}
    for record in load_records(repo):
        path_rel = rel(record.path, repo)
        meta = record.metadata
        required = ("id", "type", "status", "created", "updated", "scope")
        for key in required:
            if key not in meta or meta[key] in ("", [], None):
                errors.append(f"{path_rel}: missing required frontmatter field '{key}'.")

        rid = meta.get("id")
        if isinstance(rid, str):
            if not ID_RE.fullmatch(rid):
                errors.append(f"{path_rel}: id must be lowercase kebab-case: {rid}")
            elif rid in ids:
                errors.append(f"Duplicate record id '{rid}': {rel(ids[rid], repo)} and {path_rel}")
            else:
                ids[rid] = record.path

        rtype = meta.get("type")
        if isinstance(rtype, str):
            if rtype not in ALLOWED_TYPES:
                errors.append(f"{path_rel}: invalid type '{rtype}'.")
            else:
                expected_dir = TYPE_TO_DIR[rtype]
                try:
                    category = record.path.relative_to(records_root(repo)).parts[0]
                except Exception:
                    category = ""
                if category != expected_dir:
                    errors.append(
                        f"{path_rel}: type '{rtype}' must live under records/{expected_dir}/."
                    )

        for key in ("created", "updated"):
            value = meta.get(key)
            if isinstance(value, str):
                if not ISO_DATE_RE.fullmatch(value):
                    errors.append(f"{path_rel}: {key} must use YYYY-MM-DD: {value}")
                else:
                    try:
                        dt.date.fromisoformat(value)
                    except ValueError:
                        errors.append(f"{path_rel}: invalid {key} date: {value}")

        scope = meta.get("scope")
        if scope is not None and (not isinstance(scope, list) or not all(isinstance(x, str) and x.strip() for x in scope)):
            errors.append(f"{path_rel}: scope must be a non-empty YAML-style list.")

        for pattern in SECRET_PATTERNS:
            if pattern.search(record.text):
                errors.append(f"{path_rel}: possible secret-like content matched safety validation.")
                break

    return errors, warnings


def command_validate(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    errors, warnings = validate(repo)
    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}")
    print(f"warnings={len(warnings)}")
    print(f"errors={len(errors)}")
    return 1 if errors else 0


def command_status(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    root = memory_root(repo)
    print(f"memory_root={rel(root, repo)}")
    print(f"exists={'yes' if root.exists() else 'no'}")
    if not root.exists():
        return 0
    summary = root / "SUMMARY.md"
    if summary.exists():
        data = summary.read_bytes()
        print(f"summary_lines={len(data.decode('utf-8').splitlines())}")
        print(f"summary_bytes={len(data)}")
    records = load_records(repo)
    print(f"records_total={len(records)}")
    for category in CATEGORIES:
        count = sum(1 for r in records if r.path.parent.name == category)
        print(f"records_{category}={count}")
    errors, warnings = validate(repo)
    print(f"validation_errors={len(errors)}")
    print(f"validation_warnings={len(warnings)}")
    return 1 if errors else 0


def normalize_slug(value: str) -> str:
    slug = value.strip().lower().replace("_", "-").replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug or not ID_RE.fullmatch(slug):
        raise SystemExit("Slug must resolve to lowercase kebab-case.")
    return slug


def command_create(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    ensure_structure(repo)
    rtype = args.type
    slug = normalize_slug(args.slug)
    directory = records_root(repo) / TYPE_TO_DIR[rtype]
    filename = args.filename or f"{slug}.md"
    if not filename.endswith(".md"):
        filename += ".md"
    path = directory / filename
    if path.exists():
        raise SystemExit(f"Refusing to overwrite existing record: {rel(path, repo)}")
    today = dt.date.today().isoformat()
    scope = args.scope or [slug]
    scope_lines = "\n".join(f"  - {item}" for item in scope)
    text = f"""---\nid: {slug}\ntype: {rtype}\nstatus: {args.status}\ncreated: {today}\nupdated: {today}\nscope:\n{scope_lines}\n---\n\n# {args.title}\n\n## Current state\n\nReplace this with verified durable project context.\n\n## Read when\n\nDescribe the types of tasks for which this record should be loaded.\n"""
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"created={rel(path, repo)}")
    return 0


def tokenize(query: str) -> list[str]:
    return [x for x in re.findall(r"[a-z0-9][a-z0-9_-]*", query.lower()) if len(x) > 1]


def score_record(record: Record, terms: list[str]) -> int:
    if not terms:
        return 0
    meta_text = " ".join(
        str(v) if not isinstance(v, list) else " ".join(str(x) for x in v)
        for v in record.metadata.values()
    ).lower()
    body = record.body.lower()
    name = record.path.stem.lower()
    score = 0
    for term in terms:
        score += 8 * name.count(term)
        score += 5 * meta_text.count(term)
        score += body.count(term)
    return score


def command_search(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    terms = tokenize(args.query)
    ranked = []
    for record in load_records(repo):
        score = score_record(record, terms)
        if score > 0:
            ranked.append((score, record))
    ranked.sort(key=lambda item: (-item[0], rel(item[1].path, repo)))
    for score, record in ranked[: args.limit]:
        title_match = re.search(r"^#\s+(.+)$", record.body, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else record.path.stem
        print(f"{score:04d}  {rel(record.path, repo)}  |  {title}")
    if not ranked:
        print("No matching records.")
    return 0


def command_context(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo)
    summary = memory_root(repo) / "SUMMARY.md"
    if not summary.exists():
        raise SystemExit("Memory is not initialized. Run init first.")
    print(f"READ_FIRST={rel(summary, repo)}")
    terms = tokenize(args.query)
    ranked = []
    for record in load_records(repo):
        score = score_record(record, terms)
        if score > 0:
            ranked.append((score, record))
    ranked.sort(key=lambda item: (-item[0], rel(item[1].path, repo)))
    for i, (score, record) in enumerate(ranked[: args.max_records], start=1):
        print(f"READ_{i}={rel(record.path, repo)} score={score}")
    if not ranked:
        print("READ_RECORDS=none")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project Memory helper")
    parser.add_argument("--repo", default=".", help="Project/task repository root")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Initialize .agents/MEMORY without overwriting existing files")
    p.set_defaults(func=command_init)

    p = sub.add_parser("status", help="Show memory store status")
    p.set_defaults(func=command_status)

    p = sub.add_parser("validate", help="Validate memory structure and metadata")
    p.set_defaults(func=command_validate)

    p = sub.add_parser("create", help="Create a new memory record")
    p.add_argument("--type", choices=ALLOWED_TYPES, required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--status", default="active")
    p.add_argument("--scope", action="append", help="Repeat to add scope terms")
    p.add_argument("--filename", help="Optional filename inside the type directory")
    p.set_defaults(func=command_create)

    p = sub.add_parser("search", help="Search memory records")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=command_search)

    p = sub.add_parser("context", help="Print a compact retrieval plan for a query")
    p.add_argument("--query", required=True)
    p.add_argument("--max-records", type=int, default=5)
    p.set_defaults(func=command_context)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
