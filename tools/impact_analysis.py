from __future__ import annotations

import re
import sys
from collections import defaultdict, deque
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^(SRC|CLM|TEST|BENCH|EXP|SEC|ADR|DM)-[A-Z0-9-]+$")

BAD_STATES = {"stale", "superseded", "withdrawn", "failed", "disputed"}
FAST_PATH_VALUES = {"FAST", "fast", "fast-path", "fast_path", "reusable"}


def iter_records():
    for path in ROOT.rglob("*.yaml"):
        if "templates" in path.parts or ".github" in path.parts:
            continue
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        rid = data.get("id") or data.get("record_id")
        if rid and ID_RE.match(str(rid)):
            yield str(rid), path.relative_to(ROOT), data


def collect_refs(value):
    refs = set()
    if isinstance(value, dict):
        for nested in value.values():
            refs |= collect_refs(nested)
    elif isinstance(value, list):
        for nested in value:
            refs |= collect_refs(nested)
    elif isinstance(value, str) and ID_RE.match(value):
        refs.add(value)
    return refs


def status_tokens(data):
    tokens = set()
    for key in ("status", "state"):
        value = data.get(key)
        if isinstance(value, str):
            tokens.add(value.lower())

    for section_name in ("verification", "review", "strength", "current_decision"):
        section = data.get(section_name)
        if isinstance(section, dict):
            for key in ("status", "state"):
                value = section.get(key)
                if isinstance(value, str):
                    tokens.add(value.lower())
    return tokens


def main() -> int:
    records = {}
    reverse = defaultdict(set)

    for rid, path, data in iter_records():
        records[rid] = (path, data)

    for rid, (_, data) in records.items():
        for ref in collect_refs(data):
            if ref != rid:
                reverse[ref].add(rid)

    unhealthy = {
        rid for rid, (_, data) in records.items()
        if status_tokens(data) & BAD_STATES
    }

    if not unhealthy:
        print("Impact analysis: no stale/disputed/failed/superseded/withdrawn evidence found.")
        return 0

    impacted_by = defaultdict(set)
    queue = deque((rid, rid) for rid in sorted(unhealthy))
    visited_pairs = set(queue)

    while queue:
        current, root = queue.popleft()
        for dependent in reverse.get(current, ()): 
            impacted_by[dependent].add(root)
            pair = (dependent, root)
            if pair not in visited_pairs:
                visited_pairs.add(pair)
                queue.append(pair)

    print("Knowledge impact analysis\n")
    print("Unhealthy evidence:")
    for rid in sorted(unhealthy):
        path, data = records[rid]
        print(f"- {rid} [{', '.join(sorted(status_tokens(data) & BAD_STATES))}] -> {path}")

    if impacted_by:
        print("\nTransitive impact:")
        for rid in sorted(impacted_by):
            path, data = records[rid]
            roots = ", ".join(sorted(impacted_by[rid]))
            print(f"- {rid} <- {roots} -> {path}")

            if rid.startswith("DM-"):
                retrieval = data.get("retrieval") or {}
                path_value = retrieval.get("path")
                reusability = data.get("reusability")
                if path_value in FAST_PATH_VALUES or reusability in FAST_PATH_VALUES:
                    print(f"  ERROR: {rid} remains FAST/reusable while depending on unhealthy evidence")

    violations = []
    for rid, roots in impacted_by.items():
        if not rid.startswith("DM-"):
            continue
        _, data = records[rid]
        retrieval = data.get("retrieval") or {}
        path_value = retrieval.get("path")
        reusability = data.get("reusability")
        if path_value in FAST_PATH_VALUES or reusability in FAST_PATH_VALUES:
            violations.append((rid, roots))

    if violations:
        print("\nImpact gate FAILED: FAST PATH contains records with unhealthy transitive evidence.")
        return 1

    print("\nImpact gate PASSED: affected knowledge is traceable and no impacted DM remains FAST/reusable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
