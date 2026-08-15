from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "provenance" / "nkcki-2026-artifact-provenance-regression-v1.yaml"
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def evaluate(case_input: dict) -> str:
    requested_status = case_input.get("requested_status")
    requested_assertion = case_input.get("requested_assertion")
    source_kind = case_input.get("source_kind")

    if requested_assertion == "FIELD_LEVEL_SCHEMA_COMPLETE":
        if not case_input.get("bytes_preserved"):
            return "BLOCK_FIELD_LEVEL_COMPLETENESS"

    if requested_status == "PRIMARY_WEB_OPERATIONAL_GUIDANCE":
        if source_kind == "DYNAMIC_OFFICIAL_WEB_FORM":
            return (
                "ALLOW_TIME_BOUNDED_WEB_OBSERVATION"
                if case_input.get("observed_at")
                else "REQUIRE_OBSERVATION_TIME"
            )

    if requested_status == "IMMUTABLE_PRIMARY":
        if source_kind in {"SEARCH_ENGINE_EXCERPT", "THIRD_PARTY_MIRROR"}:
            return "BLOCK_IMMUTABLE_PRIMARY"
        if not case_input.get("bytes_preserved"):
            return "BLOCK_IMMUTABLE_PRIMARY"
        sha = case_input.get("sha256")
        if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
            return "BLOCK_IMMUTABLE_PRIMARY"
        if not case_input.get("retrieved_at"):
            return "BLOCK_IMMUTABLE_PRIMARY"
        return "ALLOW_IMMUTABLE_PRIMARY"

    return "UNHANDLED"


def main() -> int:
    data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data.get("cases", []):
        actual = evaluate(case.get("input", {}))
        expected = case.get("expected")
        if actual != expected:
            failures.append((case.get("id"), expected, actual))

    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        return 1

    print(f"PASS: {len(data.get('cases', []))} NKTsKI provenance regression cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
