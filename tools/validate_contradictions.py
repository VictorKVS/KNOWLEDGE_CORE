from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

VALID_STATES = {"OPEN", "CONTEXT_SPLIT", "RESOLVED", "ACCEPTED_UNCERTAINTY"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "contradiction":
        errors.append("kind must be contradiction")
    state = str(record.get("status", ""))
    if state not in VALID_STATES:
        errors.append(f"status must be one of {sorted(VALID_STATES)}")
    if not record.get("topic"):
        errors.append("topic is required")

    sides = list_value(record.get("sides"))
    if len(sides) < 2:
        errors.append("at least two conflicting sides are required")
    for index, side in enumerate(sides):
        if not isinstance(side, dict):
            errors.append(f"sides[{index}] must be an object")
            continue
        if not side.get("conclusion"):
            errors.append(f"sides[{index}].conclusion is required")
        if not list_value(side.get("evidence_refs")):
            errors.append(f"sides[{index}] requires evidence_refs")

    comparison = record.get("comparison") if isinstance(record.get("comparison"), dict) else {}
    if comparison.get("equivalent_context") not in {True, False, "unknown"}:
        errors.append("comparison.equivalent_context must be true, false or unknown")

    impact = record.get("impact") if isinstance(record.get("impact"), dict) else {}
    if state == "OPEN" and impact.get("fast_path_blocked") is not True:
        errors.append("OPEN contradiction must block FAST path")

    resolution = record.get("resolution") if isinstance(record.get("resolution"), dict) else {}
    resolution_state = str(resolution.get("state", state))
    if resolution_state not in VALID_STATES:
        errors.append("resolution.state is invalid")
    if state in {"RESOLVED", "CONTEXT_SPLIT"} and not resolution.get("rationale"):
        errors.append(f"{state} contradiction requires resolution.rationale")
    if state == "CONTEXT_SPLIT" and not list_value(resolution.get("context_branches")):
        errors.append("CONTEXT_SPLIT requires context_branches")
    if state == "RESOLVED" and not (
        list_value(resolution.get("winning_claims")) or list_value(resolution.get("new_evidence_refs"))
    ):
        errors.append("RESOLVED requires winning_claims or new_evidence_refs")

    review = record.get("review") if isinstance(record.get("review"), dict) else {}
    completed = set(map(str, list_value(review.get("completed_by"))))
    if review.get("analyst_required") is True and state == "RESOLVED" and "analyst" not in completed:
        errors.append("analyst review required before RESOLVED")
    if review.get("security_required") is True and state == "RESOLVED" and "security" not in completed:
        errors.append("security review required before RESOLVED")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate contradiction records")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        errors = validate(load(path))
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
