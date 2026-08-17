from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "security-knowledge" / "classification" / "fstec-kii-2025-version-routing-regression-v1.json"
BOUNDARY = date.fromisoformat("2025-09-01")


def route(case: dict) -> str:
    d = date.fromisoformat(case["date"])
    op = case["operation"]
    if op == "registry_fields":
        return "ORDER_254_CURRENT" if d >= BOUNDARY else "PRE_254_EDITION"
    if op == "categorization_form":
        return "ORDER_247_CURRENT" if d >= BOUNDARY else "PRE_247_EDITION"
    if op == "typical_sector_object_field":
        return "REQUIRED_CURRENT_FORM_FIELD" if d >= BOUNDARY else "NOT_PROVEN"
    if op == "typical_sector_object_implies_category":
        return "FALSE"
    if op == "security_means_absent":
        return "REPORT_ABSENCE_DO_NOT_INVENT_CERTIFICATION"
    if op == "exact_official_bytes_available":
        return "PENDING"
    if op == "registry_recipient_scope":
        return "SECTOR_OR_COMPETENCE_LIMITED_WHERE_APPLICABLE"
    return "NOT_PROVEN"


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = route(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected} actual={actual}")
        return 1
    print(f"PASS {len(data['cases'])} FSTEC KII 2025 version-routing cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
