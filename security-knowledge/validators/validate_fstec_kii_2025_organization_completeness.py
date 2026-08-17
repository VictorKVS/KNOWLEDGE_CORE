from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "security-knowledge" / "classification" / "fstec-kii-2025-organization-completeness-regression-v1.json"
BOUNDARY = date.fromisoformat("2025-09-01")


def evaluate(case: dict) -> str:
    d = date.fromisoformat(case["date"])
    if d < BOUNDARY:
        return "PRE_247_EDITION_ROUTING_REQUIRED"
    if case.get("category_claim") == "AUTO_FROM_TYPICAL_OBJECT":
        return "REJECT_AUTOMATIC_CATEGORY_INFERENCE"
    if not case.get("subject_scope_known", False):
        return "NOT_PROVEN_SUBJECT_APPLICABILITY"
    required = [
        ("sphere_present", "INCOMPLETE_SPHERE"),
        ("typical_sector_object_present", "INCOMPLETE_TYPICAL_SECTOR_OBJECT"),
        ("external_network_identity_present", "INCOMPLETE_EXTERNAL_NETWORK_IDENTITY"),
        ("component_present", "INCOMPLETE_COMPONENT"),
        ("hardware_inventory_present", "INCOMPLETE_HARDWARE_INVENTORY"),
    ]
    for field, result in required:
        if not case.get(field, False):
            return result
    if case.get("security_means_state") not in {"CERTIFIED", "ABSENT", "NOT_ASSESSED"}:
        return "INCOMPLETE_SECURITY_MEANS_STATE"
    return "CURRENT_FORM_MINIMUM_SEMANTIC_SET_COMPLETE"


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected} actual={actual}")
        return 1
    print(f"PASS {len(data['cases'])} FSTEC KII organization-completeness cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
