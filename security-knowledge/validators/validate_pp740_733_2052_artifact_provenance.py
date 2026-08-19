#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "security-knowledge/provenance/pp740-733-2052-official-artifact-acquisition-manifest-v1.yaml"
FIXTURES = ROOT / "security-knowledge/provenance/pp740-733-2052-official-artifact-provenance-regression-v1.yaml"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def evaluate(case: dict) -> str:
    assertion = case.get("requested_assertion")
    status = case.get("requested_status")
    source = case.get("source_kind")
    if assertion == "ELECTRONIC_PUBLICATION_ID":
        return "ALLOW_PUBLICATION_ID" if case.get("exact_official_match") else "BLOCK_PUBLICATION_ID"
    if assertion in {"DOCUMENT_ABSENT", "DOCUMENT_REPEALED"} and source == "OFFICIAL_API_TIMEOUT":
        return "NOT_PROVEN"
    if assertion == "GUESS_ADJACENT_EO_NUMBER":
        return "BLOCK_GUESS"
    if assertion == "CURRENT_RULE_TEXT" and source == "CURRENT_TEXT":
        return "ALLOW_BOUNDED_CURRENT_TEXT_CLAIM"
    if status == "IMMUTABLE_PRIMARY":
        sha = case.get("sha256")
        if source != "OFFICIAL_ORIGIN_PDF":
            return "BLOCK_IMMUTABLE_PRIMARY"
        if not case.get("bytes_preserved") or not case.get("retrieved_at"):
            return "BLOCK_IMMUTABLE_PRIMARY"
        if not isinstance(sha, str) or not SHA256.fullmatch(sha):
            return "BLOCK_IMMUTABLE_PRIMARY"
        return "ALLOW_IMMUTABLE_PRIMARY"
    raise AssertionError(f"unhandled case: {case}")


def main() -> int:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    assert manifest["status"] == "PRIMARY_METADATA_PARTIAL_IMMUTABLE_BYTES_PENDING"
    assert len(manifest["targets"]) == 3
    assert len(manifest["provenance_rules"]) == 6
    pp740 = next(row for row in manifest["targets"] if row["logical_id"] == "RU-GOV-PP-740-2025")
    assert pp740["official_publication_id"] is None
    assert pp740["bytes_preserved"] is False and pp740["sha256"] is None
    attempt = manifest["acquisition_attempt"]
    assert attempt["result"] == "OFFICIAL_API_TOTAL_TIMEOUT_2_ATTEMPTS_X_60_SECONDS_ON_FIRST_TARGET"
    assert attempt["later_targets_attempted"] is False
    assert len(fixtures["cases"]) == 12
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        return 1
    print("PASS: 3 acquisition targets; 6 provenance rules; 12 fail-closed cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
