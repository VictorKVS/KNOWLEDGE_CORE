from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

HORIZON_ORDER = {"NOW": 0, "NEXT": 1, "RESEARCH": 2, "LATER": 3}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "security-roadmap-item":
        return ["kind must be security-roadmap-item"]

    source = record.get("source") if isinstance(record.get("source"), dict) else {}
    plan = record.get("plan") if isinstance(record.get("plan"), dict) else {}
    execution = record.get("execution") if isinstance(record.get("execution"), dict) else {}
    effect = record.get("expected_effect") if isinstance(record.get("expected_effect"), dict) else {}

    if not any(as_list(source.get(k)) for k in ("priority_refs", "risk_refs", "finding_refs", "requirement_refs", "coverage_gap_refs")):
        errors.append("roadmap item requires at least one evidence-backed source reference")
    for key in ("title", "objective", "horizon", "owner_role"):
        if not plan.get(key):
            errors.append(f"plan.{key} is required")
    if str(plan.get("horizon", "")).upper() not in HORIZON_ORDER:
        errors.append("plan.horizon must be NOW, NEXT, LATER or RESEARCH")
    if str(plan.get("horizon", "")).upper() != "RESEARCH":
        if not as_list(execution.get("acceptance_criteria")):
            errors.append("committed implementation work requires acceptance_criteria")
        if not (as_list(execution.get("verification_refs")) or as_list(execution.get("verification_plan"))):
            errors.append("committed implementation work requires verification")
    risk_reduction = effect.get("risk_reduction") if isinstance(effect.get("risk_reduction"), dict) else {}
    if risk_reduction.get("bounded") is not True:
        errors.append("expected risk reduction must be explicitly bounded")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize security roadmap items")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    failed = False
    for path in args.paths:
        record = load(path)
        errors = validate(record)
        failed = failed or bool(errors)
        plan = record.get("plan") if isinstance(record.get("plan"), dict) else {}
        rows.append({
            "id": record.get("id", path.stem),
            "title": plan.get("title", ""),
            "horizon": str(plan.get("horizon", "LATER")).upper(),
            "owner": plan.get("owner_role", ""),
            "due": (plan.get("target_window") or {}).get("due", "") if isinstance(plan.get("target_window"), dict) else "",
            "blockers": as_list(plan.get("blockers")),
            "errors": errors,
            "path": str(path),
        })

    rows.sort(key=lambda r: (HORIZON_ORDER.get(r["horizon"], 99), r["due"] or "9999", r["id"]))
    if args.json:
        print(json.dumps({"items": rows, "by_horizon": dict(Counter(r["horizon"] for r in rows))}, indent=2, ensure_ascii=False))
    else:
        for row in rows:
            marker = "FAIL" if row["errors"] else "OK"
            print(f"{marker:4} {row['horizon']:8} {row['id']} owner={row['owner']} due={row['due']} {row['title']}")
            for error in row["errors"]:
                print(f"     - {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
