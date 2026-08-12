from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_corpus(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "security-regulatory-corpus":
        return ["kind must be security-regulatory-corpus"]
    scope = record.get("scope") if isinstance(record.get("scope"), dict) else {}
    extraction = record.get("extraction") if isinstance(record.get("extraction"), dict) else {}
    coverage = record.get("coverage") if isinstance(record.get("coverage"), dict) else {}
    quality = record.get("quality") if isinstance(record.get("quality"), dict) else {}
    if not record.get("name"):
        errors.append("name is required")
    if not record.get("jurisdiction"):
        errors.append("jurisdiction is required")
    if not as_list(scope.get("included_source_refs")):
        errors.append("scope.included_source_refs is required")
    if str(record.get("status", "DRAFT")).upper() in {"ACTIVE", "VERIFIED"}:
        if not as_list(extraction.get("ingestion_refs")):
            errors.append("active corpus requires ingestion_refs")
        if str(quality.get("source_health", "UNKNOWN")).upper() != "GREEN":
            errors.append("active corpus requires GREEN source_health")
        if coverage.get("unresolved_fragments"):
            errors.append("active corpus cannot hide unresolved_fragments")
    return errors


def validate_diff(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "security-source-diff":
        return ["kind must be security-source-diff"]
    lineage = record.get("source_lineage") if isinstance(record.get("source_lineage"), dict) else {}
    impact = record.get("requirement_impact") if isinstance(record.get("requirement_impact"), dict) else {}
    for field in ("old_source_ref", "new_source_ref"):
        if not lineage.get(field):
            errors.append(f"source_lineage.{field} is required")
    if lineage.get("old_source_ref") == lineage.get("new_source_ref") and lineage.get("old_source_ref"):
        errors.append("old_source_ref and new_source_ref must differ")
    if str(record.get("status", "DRAFT")).upper() in {"REVIEWED", "VERIFIED"}:
        if not any(as_list(impact.get(k)) for k in (
            "unchanged_requirements", "modified_requirements", "retired_requirements", "new_requirements", "needs_manual_review"
        )):
            errors.append("reviewed diff requires explicit requirement impact classification")
    return errors


def validate(record: dict[str, Any]) -> list[str]:
    kind = record.get("kind")
    if kind == "security-regulatory-corpus":
        return validate_corpus(record)
    if kind == "security-source-diff":
        return validate_diff(record)
    return ["unsupported kind"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate regulatory corpus and source-diff records")
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
