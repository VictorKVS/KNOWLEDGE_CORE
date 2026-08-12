from __future__ import annotations

import argparse
import json
from pathlib import Path

from knowledge_runtime import KnowledgeRuntime, RuntimeConfig


def main() -> int:
    parser = argparse.ArgumentParser(description="Local Father Knowledge Runtime")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--index", type=Path, default=Path("generated/knowledge-index.json"))

    sub = parser.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get")
    p_get.add_argument("record_id")

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--kind", action="append", default=[])
    p_search.add_argument("--limit", type=int, default=10)

    p_graph = sub.add_parser("graph")
    p_graph.add_argument("record_id")
    p_graph.add_argument("--depth", type=int, default=1)

    p_impacts = sub.add_parser("impacts")
    p_impacts.add_argument("record_id")

    p_brief = sub.add_parser("brief")
    p_brief.add_argument("query")
    p_brief.add_argument("--owner-agent", default="programming_agent")
    p_brief.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()
    runtime = KnowledgeRuntime(RuntimeConfig(root=args.root, index_path=args.index))

    if args.command == "get":
        result = runtime.get_record(args.record_id)
    elif args.command == "search":
        result = runtime.search(args.query, kinds=set(args.kind), limit=args.limit)
    elif args.command == "graph":
        result = runtime.neighborhood(args.record_id, depth=args.depth)
    elif args.command == "impacts":
        result = runtime.impacts(args.record_id)
    elif args.command == "brief":
        result = runtime.build_decision_brief(query=args.query, owner_agent=args.owner_agent, limit=args.limit)
    else:
        raise AssertionError(args.command)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
