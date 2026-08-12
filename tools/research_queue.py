from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

WEIGHT = {
    "decision_criticality": {"low": 1, "medium": 2, "high": 4, "critical": 7},
    "uncertainty": {"low": 1, "medium": 2, "high": 4},
    "reversibility": {"easy": 1, "moderate": 2, "hard": 4},
    "blast_radius": {"local": 1, "component": 2, "system": 4, "organization": 7},
}
COST = {"low": 1, "medium": 2, "high": 4}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def priority_score(record: dict[str, Any]) -> float:
    p = record.get("priority") if isinstance(record.get("priority"), dict) else {}
    benefit = sum(
        WEIGHT[field].get(str(p.get(field, "medium")), 0)
        for field in ("decision_criticality", "uncertainty", "reversibility", "blast_radius")
    )
    cost = COST.get(str(p.get("evidence_cost", "medium")), 2)
    return round(benefit / cost, 2)


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "research-task":
        errors.append("kind must be research-task")
    gap = record.get("gap") if isinstance(record.get("gap"), dict) else {}
    scope = record.get("scope") if isinstance(record.get("scope"), dict) else {}
    route = record.get("route") if isinstance(record.get("route"), dict) else {}
    for field in ("type", "statement", "why_it_matters"):
        if not gap.get(field):
            errors.append(f"gap.{field} is required")
    if not scope.get("question"):
        errors.append("scope.question is required")
    if not route.get("owner_role"):
        errors.append("route.owner_role is required")
    if not scope.get("stop_when"):
        errors.append("scope.stop_when is required to bound research")
    result = record.get("result") if isinstance(record.get("result"), dict) else {}
    if str(record.get("status", "OPEN")).upper() == "CLOSED":
        if not result.get("produced_evidence_refs"):
            errors.append("closed research task requires produced_evidence_refs")
        if not result.get("summary"):
            errors.append("closed research task requires result.summary")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and prioritize evidence-gap research tasks")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = []
    failed = False
    for path in args.paths:
        record = load(path)
        errors = validate(record)
        failed = failed or bool(errors)
        rows.append({
            "id": record.get("id", path.stem),
            "title": record.get("title", ""),
            "status": record.get("status", ""),
            "owner": (record.get("route") or {}).get("owner_role", "") if isinstance(record.get("route"), dict) else "",
            "score": priority_score(record),
            "errors": errors,
            "path": str(path),
        })

    rows.sort(key=lambda item: item["score"], reverse=True)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for row in rows:
            marker = "FAIL" if row["errors"] else "OK"
            print(f"{marker:4} score={row['score']:>5} {row['id']} owner={row['owner']} {row['title']}")
            for error in row["errors"]:
                print(f"     - {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
