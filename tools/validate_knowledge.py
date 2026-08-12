from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STABLE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")

EXCLUDED_PARTS = {"templates", ".github"}
STRICT_ID_ROOTS = {
    "algorithms",
    "data-structures",
    "problems",
    "benchmarks",
    "decisions",
    "decision-memory",
    "sources",
    "claims",
    "experiments",
}
PROMOTED_STATUSES = {"MEASURED", "VERIFIED", "REUSABLE"}
EVIDENCE_STATES = {"DOCUMENTED", "MEASURED", "DERIVED", "EXPERT_ESTIMATE", "UNKNOWN"}


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


def validate_stable_id(rel: Path, rid: str, errors: list[str]):
    if rel.parts and rel.parts[0] in STRICT_ID_ROOTS and not STABLE_ID_RE.match(rid):
        errors.append(f"{rel}: invalid stable id format: {rid}")


def validate_source(path: Path, data: dict, errors: list[str]):
    verification = data.get("verification") or {}
    status = str(verification.get("status", "")).lower()
    access = data.get("access") or {}
    identifiers = data.get("identifiers") or {}

    if status == "verified":
        has_locator = bool(access.get("canonical_url")) or any(
            bool(identifiers.get(key)) for key in ("doi", "isbn", "rfc", "standard", "official_id")
        )
        if not has_locator:
            errors.append(f"{path}: verified source requires canonical_url or authoritative identifier")
        if not verification.get("checked_at"):
            errors.append(f"{path}: verified source requires checked_at")


def validate_claim(path: Path, data: dict, errors: list[str]):
    strength = data.get("strength") or {}
    state = str(strength.get("state", "UNKNOWN")).upper()
    supporting = data.get("supporting_evidence") or {}
    reasoning = data.get("reasoning") or {}

    if state not in EVIDENCE_STATES:
        errors.append(f"{path}: invalid evidence state {state}")
        return

    if state == "DOCUMENTED" and not supporting.get("sources"):
        errors.append(f"{path}: DOCUMENTED claim requires supporting source ids")

    if state == "MEASURED" and not (supporting.get("benchmarks") or supporting.get("experiments")):
        errors.append(f"{path}: MEASURED claim requires benchmark or experiment evidence")

    if state == "DERIVED":
        if not reasoning.get("derivation"):
            errors.append(f"{path}: DERIVED claim requires explicit derivation")
        if not reasoning.get("assumptions"):
            errors.append(f"{path}: DERIVED claim requires explicit assumptions")

    if state == "EXPERT_ESTIMATE" and not reasoning.get("derivation"):
        errors.append(f"{path}: EXPERT_ESTIMATE requires visible rationale in reasoning.derivation")


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
            validate_stable_id(rel, rid, errors)
            if rel.parts and rel.parts[0] in STRICT_ID_ROOTS:
                if rid in ids:
                    errors.append(f"{rel}: duplicate id {rid}; first seen in {ids[rid].relative_to(ROOT)}")
                else:
                    ids[rid] = path

        if isinstance(data, dict):
            root = rel.parts[0] if rel.parts else ""
            if root == "decision-memory":
                validate_decision_memory(rel, data, errors)
            elif root == "sources":
                validate_source(rel, data, errors)
            elif root == "claims":
                validate_claim(rel, data, errors)

            if str(data.get("status", "")).upper() == "MEASURED" and root not in {"decision-memory", "claims"}:
                benchmark_id = data.get("benchmark_id") or data.get("benchmark")
                if not has_nonempty(benchmark_id):
                    errors.append(f"{rel}: MEASURED record requires benchmark_id/benchmark reference")

    if errors:
        print("Knowledge quality gate FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Knowledge quality gate PASSED. Validated {len(ids)} stable evidence IDs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
