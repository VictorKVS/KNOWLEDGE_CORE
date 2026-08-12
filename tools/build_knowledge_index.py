from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

import yaml

ID_RE = re.compile(r"^(SRC|CLM|TEST|BENCH|EXP|ADR|DM|CTX|DPK|OUT|PROM|CON|RQ)-[A-Za-z0-9_.-]+$")
SKIP_DIRS = {".git", ".github", "templates", "node_modules", ".venv", "venv"}


def walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)
    else:
        yield value


def refs(record: dict[str, Any], own_id: str) -> list[str]:
    found: set[str] = set()
    for value in walk_values(record):
        if isinstance(value, str) and ID_RE.match(value) and value != own_id:
            found.add(value)
    return sorted(found)


def load_yaml(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError):
        return None
    return value if isinstance(value, dict) else None


def infer_kind(record_id: str) -> str:
    return record_id.split("-", 1)[0]


def build(root: Path) -> dict[str, Any]:
    nodes: dict[str, Any] = {}
    duplicates: dict[str, list[str]] = {}
    for path in root.rglob("*.y*ml"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        record = load_yaml(path)
        if not record:
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not ID_RE.match(record_id):
            continue
        rel = path.relative_to(root).as_posix()
        if record_id in nodes:
            duplicates.setdefault(record_id, [nodes[record_id]["path"]]).append(rel)
            continue
        nodes[record_id] = {
            "id": record_id,
            "kind": infer_kind(record_id),
            "path": rel,
            "status": record.get("status", ""),
            "title": record.get("title") or record.get("name") or record.get("topic") or "",
            "tags": record.get("tags", []) if isinstance(record.get("tags"), list) else [],
            "health": record.get("health", ""),
            "refs": refs(record, record_id),
        }

    unresolved: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    for node in nodes.values():
        for target in node["refs"]:
            edges.append({"from": node["id"], "to": target})
            if target not in nodes:
                unresolved.append({"from": node["id"], "to": target})

    return {
        "schema_version": "1.0",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": edges,
        "unresolved_refs": unresolved,
        "duplicate_ids": duplicates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build compact knowledge graph index")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("generated/knowledge-index.json"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    index = build(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"nodes={index['node_count']} edges={index['edge_count']} unresolved={len(index['unresolved_refs'])}")
    if index["duplicate_ids"]:
        print(f"duplicate_ids={len(index['duplicate_ids'])}")
    return 1 if args.strict and (index["unresolved_refs"] or index["duplicate_ids"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
