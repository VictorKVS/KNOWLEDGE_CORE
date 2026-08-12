from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


FAST_STATES = {"FAST", "FAST_ELIGIBLE", "fast", "fast_eligible"}
APPROVED = {"approved", "verified", "reusable", "fast_eligible"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "knowledge-promotion":
        errors.append("kind must be knowledge-promotion")

    subject = record.get("subject") if isinstance(record.get("subject"), dict) else {}
    for key in ("id", "kind", "current_state", "proposed_state"):
        if not subject.get(key):
            errors.append(f"subject.{key} is required")

    requirements = record.get("requirements") if isinstance(record.get("requirements"), dict) else {}
    missing = as_list(requirements.get("missing"))
    hard_blocks = as_list(requirements.get("hard_blocks"))

    result = record.get("result") if isinstance(record.get("result"), dict) else {}
    decision = str(result.get("decision", "pending")).lower()
    proposed = str(subject.get("proposed_state", ""))

    if decision == "approved" and missing:
        errors.append("approved promotion cannot have missing requirements")
    if decision == "approved" and hard_blocks:
        errors.append("approved promotion cannot have hard blocks")
    if decision == "approved" and not result.get("reason"):
        errors.append("approved promotion requires result.reason")

    evidence = record.get("supporting_evidence") if isinstance(record.get("supporting_evidence"), dict) else {}
    evidence_count = sum(len(as_list(evidence.get(key))) for key in (
        "sources", "claims", "tests", "benchmarks", "experiments", "security_reviews", "outcomes"
    ))
    if decision == "approved" and evidence_count == 0:
        errors.append("approved promotion requires supporting evidence")

    applicability = record.get("applicability") if isinstance(record.get("applicability"), dict) else {}
    if decision == "approved" and proposed in FAST_STATES:
        if not applicability.get("envelope") and not as_list(applicability.get("inherited_from")):
            errors.append("FAST promotion requires applicability envelope or inherited applicability")
        refs = set(as_list(evidence.get("claims")) + as_list(evidence.get("outcomes")))
        if not refs:
            errors.append("FAST promotion requires claim/outcome evidence")

    review = record.get("review") if isinstance(record.get("review"), dict) else {}
    required_roles = set(map(str, as_list(review.get("required_roles"))))
    completed = set(map(str, as_list(review.get("completed_by"))))
    if decision == "approved" and required_roles - completed:
        errors.append("required promotion reviews are incomplete")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate knowledge promotion records")
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
