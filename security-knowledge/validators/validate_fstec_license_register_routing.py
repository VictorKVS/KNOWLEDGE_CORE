from __future__ import annotations

from pathlib import Path
import sys
import yaml

FIXTURES = Path(__file__).resolve().parents[1] / "lifecycle" / "fstec-license-register-routing-regression-v1.yaml"


def route(case: dict) -> str:
    query = case.get("query_kind")
    source = case.get("source_kind")
    snapshot = case.get("snapshot_date")
    decision = case.get("decision_date")

    if query == "CURRENT_SZI_CERTIFICATE_VALIDITY":
        return "ROUTE_TO_FSTEC_CERTIFICATE_REGISTER"

    if query == "CURRENT_ORGANIZATION_LICENSE_VALIDITY":
        if source == "CURRENT_AUTHORITATIVE_LICENSE_RECORD" and snapshot and decision and snapshot == decision:
            return "ALLOW_RECORD_LEVEL_EVALUATION"
        return "REQUIRE_CURRENT_AUTHORITATIVE_LICENSE_RECORD"

    if query == "HISTORICAL_ORGANIZATION_LICENSE_STATUS":
        if source == "HASH_PINNED_REGISTER_SNAPSHOT" and snapshot and decision and snapshot == decision:
            return "ALLOW_TIME_BOUNDED_EVALUATION"
        return "REQUIRE_TIME_BOUNDED_AUTHORITATIVE_RECORD"

    return "NEEDS_LIFECYCLE_REVIEW"


def main() -> int:
    data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = route(case)
        expected = case["expected"]
        if actual != expected:
            failures.append((case["id"], expected, actual))
    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        return 1
    print(f"PASS: {len(data['cases'])} FSTEC license-register routing cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
