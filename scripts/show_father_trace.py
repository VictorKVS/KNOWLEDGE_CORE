# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

DEFAULT_TRACE_ROOT = Path(r"G:\1\FATHER_KNOWLEDGE\traces")
DEFAULT_DB = Path(r"G:\1\FATHER_KNOWLEDGE\db\father_knowledge.db")


def load_events(path: Path) -> list[dict]:
    events = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            events.append(json.loads(line))
        except Exception:
            events.append({"status": "ERROR", "stage": "TRACE_PARSE", "error_message": line[:500]})
    return events


def main() -> int:
    p = argparse.ArgumentParser(description="Show FATHER trace summary and failures")
    p.add_argument("trace_id", nargs="?")
    p.add_argument("--root", default=str(DEFAULT_TRACE_ROOT))
    p.add_argument("--db", default=str(DEFAULT_DB))
    args = p.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Trace root not found: {root}")
        return 2

    if args.trace_id:
        path = root / f"{args.trace_id}.jsonl"
    else:
        files = sorted(root.glob("TRACE-*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not files:
            print("No trace files found")
            return 2
        path = files[0]

    if not path.exists():
        print(f"Trace not found: {path}")
        return 2

    events = load_events(path)
    trace_id = events[0].get("trace_id") if events else path.stem
    print(f"TRACE_ID: {trace_id}")
    print(f"FILE:     {path}")
    print(f"EVENTS:   {len(events)}")

    by_status = {}
    for e in events:
        by_status[e.get("status")] = by_status.get(e.get("status"), 0) + 1
    print("STATUS:", json.dumps(by_status, ensure_ascii=False))

    print("\nSTAGES:")
    seen = []
    for e in events:
        key = (e.get("stage"), e.get("span_id"), e.get("status"))
        if key not in seen and e.get("event") != "STDOUT":
            seen.append(key)
            print(f"  {e.get('timestamp')} | {e.get('status'):7} | {e.get('stage'):24} | span={e.get('span_id')} | entity={e.get('entity_type')}:{e.get('entity_id')}")

    failures = [e for e in events if e.get("status") in {"ERROR", "BLOCKED"}]
    print(f"\nFAILURES: {len(failures)}")
    for e in failures:
        print(f"  {e.get('stage')} | {e.get('error_type')} | {e.get('error_message')} | span={e.get('span_id')}")

    db = Path(args.db)
    if db.exists():
        try:
            conn = sqlite3.connect(db)
            rows = conn.execute(
                "SELECT entity_type, entity_id, trace_id, span_id, relation FROM entity_trace_links WHERE trace_id=? ORDER BY entity_type, entity_id",
                (trace_id,),
            ).fetchall()
            conn.close()
            print(f"\nENTITY LINKS: {len(rows)}")
            for row in rows[:100]:
                print("  " + " | ".join(str(x) for x in row))
        except Exception as exc:
            print(f"\nDB trace lookup unavailable: {type(exc).__name__}: {exc}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
