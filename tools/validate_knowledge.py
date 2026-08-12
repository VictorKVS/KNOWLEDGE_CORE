from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STABLE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
TRACE_REF_RE = re.compile(r"^(CLM|SRC|BENCH|EXP|TEST|SEC|ADR|DM)-[A-Z0-9-]+$")
RESOLVABLE_PREFIXES = {"CLM", "SRC", "BENCH", "EXP", "TEST", "ADR", "DM"}

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
    "tests",
}
PROMOTED_STATUSES = {"MEASURED", "VERIFIED", "REUSABLE"}
EVIDENCE_STATES = {"DOCUMENTED", "MEASURED", "DERIVED", "EXPERT_ESTIMATE", "UNKNOWN"}
MATURE_DECISION_STATUSES = {"REVIEWED", "VERIFIED", "APPROVED", "ADOPTED", "REUSABLE"}


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


def validate_test(path: Path, data: dict, errors: list[str]):
    status = str(data.get("status", "")).lower()
    contract = data.get("contract") or {}
    implementations = data.get("implementations") or []
    execution = data.get("execution") or {}

    if status in {"active", "verified", "reusable"}:
        if not contract.get("verifies"):
            errors.append(f"{path}: active test evidence requires contract.verifies")
        if not implementations:
            errors.append(f"{path}: active test evidence requires implementation paths")
        if not execution.get("ci_workflow"):
            errors.append(f"{path}: active test evidence requires execution.ci_workflow")


def _validate_reason_items(path: Path, label: str, items, errors: list[str]):
    if not isinstance(items, list):
        errors.append(f"{path}: {label} must be a list")
        return
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{path}: {label}[{idx}] must be an object")
            continue
        if not item.get("because"):
            errors.append(f"{path}: {label}[{idx}] requires because")
        supports = item.get("supports") or []
        if not supports:
            errors.append(f"{path}: {label}[{idx}] requires at least one traceable support reference")
        for ref in supports:
            if not TRACE_REF_RE.match(str(ref)):
                errors.append(f"{path}: {label}[{idx}] has invalid support reference {ref}")


def validate_decision(path: Path, data: dict, errors: list[str]):
    status = str(data.get("status", "")).upper()
    decision = data.get("decision") or {}
    selected = decision.get("selected")
    reasons = data.get("reason_chain") or []
    rejections = data.get("rejection_reason_chain") or []

    if status in MATURE_DECISION_STATUSES:
        if not selected:
            errors.append(f"{path}: mature decision requires decision.selected")
        if not reasons:
            errors.append(f"{path}: mature decision requires reason_chain")
        else:
            _validate_reason_items(path, "reason_chain", reasons, errors)

        rejected_options = decision.get("rejected_options") or []
        if rejected_options:
            if not rejections:
                errors.append(f"{path}: mature decision with rejected_options requires rejection_reason_chain")
            else:
                _validate_reason_items(path, "rejection_reason_chain", rejections, errors)
                explained = {str(item.get("option")) for item in rejections if isinstance(item, dict)}
                for option in rejected_options:
                    if str(option) not in explained:
                        errors.append(f"{path}: rejected option {option} lacks causal rejection reason")


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


def collect_refs(value: Any, refs: set[str]) -> None:
    if isinstance(value, str):
        if TRACE_REF_RE.match(value):
            refs.add(value)
        return
    if isinstance(value, list):
        for item in value:
            collect_refs(item, refs)
        return
    if isinstance(value, dict):
        for item in value.values():
            collect_refs(item, refs)


def is_strict_reference_record(root: str, data: dict) -> bool:
    status = str(data.get("status", "")).upper()
    if root == "decisions":
        return status in MATURE_DECISION_STATUSES
    if root == "tests":
        return status in {"ACTIVE", "VERIFIED", "REUSABLE"}
    if root == "decision-memory":
        return status in PROMOTED_STATUSES or str(data.get("reusability", "")).lower() in {"reusable", "fast-path", "fast_path"}
    if root == "claims":
        review = str((data.get("review") or {}).get("status", "")).upper()
        return review in {"REVIEWED", "VERIFIED"}
    if root == "sources":
        verification = str((data.get("verification") or {}).get("status", "")).upper()
        return verification == "VERIFIED"
    return False


def ref_prefix(ref: str) -> str:
    return ref.split("-", 1)[0]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    ids: dict[str, Path] = {}
    records: list[tuple[Path, dict]] = []

    for path in iter_yaml_files():
        rel = path.relative_to(ROOT)
        try:
            data = load_yaml(path)
        except Exception as exc:
            errors.append(f"{rel}: invalid YAML: {exc}")
            continue

        if isinstance(data, dict):
            records.append((rel, data))

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
            elif root == "decisions":
                validate_decision(rel, data, errors)
            elif root == "tests":
                validate_test(rel, data, errors)

            if str(data.get("status", "")).upper() == "MEASURED" and root not in {"decision-memory", "claims"}:
                benchmark_id = data.get("benchmark_id") or data.get("benchmark")
                if not has_nonempty(benchmark_id):
                    errors.append(f"{rel}: MEASURED record requires benchmark_id/benchmark reference")

    # Second pass: resolve evidence graph references after every ID is indexed.
    for rel, data in records:
        root = rel.parts[0] if rel.parts else ""
        own_id = str(record_id(data) or "")
        refs: set[str] = set()
        collect_refs(data, refs)
        refs.discard(own_id)
        strict = is_strict_reference_record(root, data)

        for ref in sorted(refs):
            if ref_prefix(ref) not in RESOLVABLE_PREFIXES:
                continue  # e.g. SEC-* awaits its dedicated registry.
            if ref not in ids:
                message = f"{rel}: unresolved evidence reference {ref}"
                if strict:
                    errors.append(message)
                else:
                    warnings.append(message)

    if warnings:
        print("Knowledge quality gate warnings:\n")
        for warning in warnings:
            print(f"- {warning}")
        print()

    if errors:
        print("Knowledge quality gate FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Knowledge quality gate PASSED. Indexed {len(ids)} stable evidence IDs with cross-reference checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
