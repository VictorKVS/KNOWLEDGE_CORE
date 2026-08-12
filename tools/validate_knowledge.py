from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")

EXCLUDED_PARTS = {"templates", ".github"}
PROMOTED_STATUSES = {"MEASURED", "VERIFIED", "REUSABLE"}


def iter_yaml_files():
    for path in ROOT.rglob("*.yaml"):
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        yield path


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def record_id(data):
    if not isinstance(data, dict):
        return None
    return data.get("id") or data.get("record_id")


def has_nonempty(value):
    if value is None:
        return False
    if isinstance(value, (list, dict, str)):
        return bool(value)
    return True


def validate_decision_memory(path: Path, data: dict, errors: list[str]):
    status = str(data.get("status", "")).upper()
    reusability = str(data.get("reusability", "")).lower()
    evidence = data.get("evidence") or {}
    measured_results = evidence.get("measured_results") or []

    if status == "PENDING_MEASUREMENT" and measured_results:
        errors.append(f"{path}: PENDING_MEASUREMENT cannot contain measured_results")

    if status in PROMOTED_STATUSES and not measured_results:
        errors.append(f"{path}: {status} requires at least one measured result")

    if reusability in {"reusable", "fast-path", "fast_path"}:
        required = data.get("promotion_rules", {}).get("reusable_fast_path_requires") or []
        required_text = " ".join(map(str, required)).lower()
        for token in ("correctness", "benchmark", "security", "environment"):
            if token not in required_text:
                errors.append(f"{path}: reusable record lacks promotion rule for {token}")

        current = data.get("current_decision") or {}
        if str(current.get("state", "")).upper() in {"NOT_FINAL", "PENDING"}:
            errors.append(f"{path}: reusable record cannot have non-final decision state")


def main() -> int:
    errors: list[str] = []
    ids: dict[str, Path] = {}

    for path in iter_yaml_files():
        rel = path.relative_to(ROOT)
        try:
            data = load_yaml(path)
        except Exception as exc:
            errors.append(f"{rel}: invalid YAML: {exc}")
            continue

        rid = record_id(data)
        if rid:
            rid = str(rid)
            if not ID_RE.match(rid):
                errors.append(f"{rel}: invalid stable id format: {rid}")
            if rid in ids:
                errors.append(f"{rel}: duplicate id {rid}; first seen in {ids[rid].relative_to(ROOT)}")
            else:
                ids[rid] = path

        if rel.parts and rel.parts[0] == "decision-memory" and isinstance(data, dict):
            validate_decision_memory(rel, data, errors)

        if isinstance(data, dict) and str(data.get("status", "")).upper() == "MEASURED":
            benchmark_id = data.get("benchmark_id") or data.get("benchmark")
            if not has_nonempty(benchmark_id) and rel.parts[0] != "decision-memory":
                errors.append(f"{rel}: MEASURED record requires benchmark_id/benchmark reference")

    if errors:
        print("Knowledge quality gate FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Knowledge quality gate PASSED. Validated {len(ids)} stable IDs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
