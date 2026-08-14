#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

FIXTURE = Path(__file__).resolve().parents[1] / "lifecycle" / "fsb-license-certificate-routing-regression-v1.yaml"


def route(case):
    q = case.get("query_type")
    x = case.get("inputs", {})
    if q == "contractor_crypto_activity_license_status":
        if not x.get("current_fsb_license_registry_record", False):
            return "FAIL_CLOSED_NEEDS_CURRENT_LICENSE_RECORD"
        if not x.get("scope_matched", False):
            return "FAIL_CLOSED_SCOPE_MISMATCH"
        return "VALIDATABLE_FROM_LICENSE_REGISTRY"
    if q == "product_FSB_certification_status":
        if not x.get("current_fsb_certified_szi_record", False):
            return "FAIL_CLOSED_NEEDS_CURRENT_CERTIFICATE_RECORD"
        if not x.get("product_version_matched", False):
            return "FAIL_CLOSED_PRODUCT_VERSION_MISMATCH"
        return "VALIDATABLE_FROM_CERTIFIED_SZI_RECORD"
    if q == "need_for_crypto_activity_license":
        if not x.get("actual_work_or_service_identified", False):
            return "NEEDS_WORK_SERVICE_CLASSIFICATION"
        if not x.get("pp313_item_matched", False):
            return "NEEDS_PP313_APPLICABILITY_REVIEW"
        if x.get("own_needs_exception_status") in (None, "unknown"):
            return "FAIL_CLOSED_NEEDS_EXCEPTION_REVIEW"
        return "DECISION_REQUIRES_COMPLETE_PP313_FACTS"
    return "FAIL_CLOSED_UNKNOWN_QUERY_TYPE"


def main():
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data.get("cases", []):
        got = route(case)
        expected = case.get("expected")
        if got != expected:
            failures.append((case.get("id"), expected, got))
    if failures:
        for cid, expected, got in failures:
            print(f"FAIL {cid}: expected={expected} got={got}")
        return 1
    print(f"PASS: {len(data.get('cases', []))} FSB license/certificate routing cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
