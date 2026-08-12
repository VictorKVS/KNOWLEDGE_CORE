from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score(node: dict[str, Any], terms: list[str], kinds: set[str], health: set[str]) -> int:
    if kinds and str(node.get("kind", "")).upper() not in kinds:
        return -1
    if health and str(node.get("health", "")).upper() not in health:
        return -1
    haystack = " ".join([
        str(node.get("id", "")),
        str(node.get("title", "")),
        " ".join(map(str, node.get("tags", []))),
        str(node.get("status", "")),
    ]).lower()
    return sum(3 if term in str(node.get("id", "")).lower() else 1 for term in terms if term in haystack)


def main() -> int:
    parser = argparse.ArgumentParser(description="Query compact knowledge graph index")
    parser.add_argument("query", nargs="*", help="search terms")
    parser.add_argument("--index", type=Path, default=Path("generated/knowledge-index.json"))
    parser.add_argument("--kind", action="append", default=[])
    parser.add_argument("--health", action="append", default=[])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--explain", action="store_true", help="include one-hop references")
    args = parser.parse_args()

    data = load(args.index)
    terms = [term.lower() for term in args.query]
    kinds = {value.upper() for value in args.kind}
    health = {value.upper() for value in args.health}

    ranked = []
    by_id = {node["id"]: node for node in data.get("nodes", [])}
    for node in data.get("nodes", []):
        value = score(node, terms, kinds, health)
        if value >= 0 and (value > 0 or not terms):
            item = dict(node)
            item["score"] = value
            if args.explain:
                item["linked"] = [by_id[ref] for ref in node.get("refs", []) if ref in by_id]
            ranked.append(item)

    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    print(json.dumps(ranked[: args.limit], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
