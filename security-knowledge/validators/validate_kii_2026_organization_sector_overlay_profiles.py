from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT
    / "security-knowledge"
    / "classification"
    / "kii-2026-organization-sector-overlay-profiles-v1.json"
)

BASE_SOURCES = ["PP_RF_127_2018", "FSTEC_ORDER_247_2025_CURRENT_FORM"]


def evaluate(case: dict, overlays: dict[str, str]) -> dict:
    subject_state = case.get("subject_state")
    if subject_state == "NOT_PROVEN":
        return {"status": "NOT_PROVEN_CII_SUBJECT", "sources": []}
    if subject_state == "NOT_CII":
        return {"status": "NOT_ROUTED_AS_CII", "sources": []}
    if subject_state != "CONFIRMED":
        return {"status": "NOT_PROVEN_CII_SUBJECT", "sources": []}

    required = [
        ("sphere_present", "INCOMPLETE_SPHERE"),
        ("typical_sector_object_present", "INCOMPLETE_TYPICAL_SECTOR_OBJECT"),
        ("external_network_identity_present", "INCOMPLETE_EXTERNAL_NETWORK_IDENTITY"),
        ("component_present", "INCOMPLETE_COMPONENT"),
        ("hardware_inventory_present", "INCOMPLETE_HARDWARE_INVENTORY"),
    ]
    for field, status in required:
        if not case.get(field, False):
            return {"status": status, "sources": BASE_SOURCES.copy()}

    if case.get("security_means_state") not in {"CERTIFIED", "ABSENT", "NOT_ASSESSED"}:
        return {
            "status": "INCOMPLETE_SECURITY_MEANS_STATE",
            "sources": BASE_SOURCES.copy(),
        }

    sectors = case.get("sectors", [])
    if not sectors:
        return {"status": "NEEDS_SECTOR_FACTS", "sources": BASE_SOURCES.copy()}

    matched = [overlays[sector] for sector in sectors if sector in overlays]
    sources = BASE_SOURCES + matched

    if case.get("category_claim") == "AUTO_FROM_TYPICAL_OBJECT":
        return {
            "status": "REJECT_AUTOMATIC_CATEGORY_INFERENCE",
            "sources": sources,
        }

    if any(sector not in overlays for sector in sectors):
        return {"status": "NEEDS_SECTOR_OVERLAY_REVIEW", "sources": sources}

    return {"status": "ROUTE", "sources": sources}


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[tuple[str, dict, dict]] = []
    for case in data["cases"]:
        actual = evaluate(case, data["verified_overlay_anchors"])
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))

    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected!r} actual={actual!r}")
        return 1

    print(
        f"PASS {len(data['cases'])} organization-to-sector overlay routing profiles"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
