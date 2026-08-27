#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/government-decrees/445/article64-content-retention-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/government-decrees/445/article64-content-retention-regression-v1.json")


POINT5_CURRENT = {
    "DATA_TRANSMISSION_FOR_VOICE_PURPOSE",
    "MOBILE_RADIOTELEPHONE",
    "LOCAL_TELEPHONE",
}
POINT6_CURRENT = {
    "DATA_TRANSMISSION_EXCEPT_FOR_VOICE_PURPOSE",
    "TELEMATIC",
}
ALL_DATA = {
    "DATA_TRANSMISSION_FOR_VOICE_PURPOSE",
    "DATA_TRANSMISSION_EXCEPT_FOR_VOICE_PURPOSE",
}


def evaluate(case):
    q = case["query"]
    if q == "version":
        return "PP1066_FUTURE_SCOPE" if date.fromisoformat(case["as_of"]) >= date(2026, 9, 1) else "PP445_CURRENT_SCOPE"
    if q == "storage_location":
        return "PASS" if case["location"] == "RUSSIA" else "BLOCK_NOT_IN_RUSSIA"
    if q == "zero_volume":
        return "ZERO_VOLUME" if case["source"] in {"MANDATORY_PUBLIC_TV_RADIO", "REGISTERED_AUDIOVISUAL_SERVICE"} else "NO_ZERO_VOLUME_ROUTE"
    if q == "other_operator_resource":
        if not case["other_operator"]:
            return "OWN_RESOURCE_ROUTE"
        return "ALLOW" if case["fsb_agreement"] else "BLOCK_FSB_AGREEMENT_MISSING"
    if q == "production_confirmation":
        return "PASS" if case["valid_at_installation"] else "BLOCK_VALID_CONFIRMATION_MISSING"
    if q == "current_service_routes":
        routes = []
        if case["service"] in POINT5_CURRENT:
            routes.append("POINT5_SIX_MONTH_FULL_VOLUME")
        if case["service"] in POINT6_CURRENT:
            routes.append("POINT6_CAPACITY_ROUTE")
        return routes
    if q == "future_service_routes":
        routes = []
        if case["service"] in POINT5_CURRENT | ALL_DATA:
            routes.append("POINT5_SIX_MONTH_FULL_VOLUME")
        if case["service"] in POINT6_CURRENT | ALL_DATA:
            routes.append("POINT6_CAPACITY_ROUTE")
        if len(routes) == 2:
            routes.append("OVERLAP_REQUIRES_INTERPRETATION")
        return routes
    if q == "point5_period":
        if case["months"] != 6:
            return "BLOCK_PERIOD_MISMATCH"
        return "PASS" if case["full_volume"] else "BLOCK_VOLUME_MISMATCH"
    if q == "point6_history":
        return "ZERO_VOLUME" if date.fromisoformat(case["as_of"]) < date(2018, 10, 1) else "CAPACITY_ROUTE"
    if q == "initial_capacity":
        if case["reference_days"] != 30:
            return "BLOCK_WRONG_REFERENCE_DAYS"
        return "PASS" if case["preceding_commissioning"] else "BLOCK_WRONG_REFERENCE_WINDOW"
    if q == "capacity_growth":
        if case["annual_percent"] != 15:
            return "BLOCK_PERCENT_MISMATCH"
        return "PASS_NO_UNSTATED_FORMULA" if case["years"] == 5 else "BLOCK_DURATION_MISMATCH"
    if q == "capacity_growth_claim":
        return "REJECT_CONFLATION" if case["claim"] == "MESSAGE_RETENTION_FIVE_YEARS" else "REJECT_UNSTATED_FORMULA"
    if q == "commissioning_act":
        return "PASS" if all(case[k] for k in ("fsb", "rkn", "operator")) else "BLOCK_SIGNATORY_MISSING"
    if q == "protection":
        return "PASS" if case["protected"] else "BLOCK_UNAUTHORIZED_ACCESS_PROTECTION_UNPROVEN"
    if q == "deletion":
        if not case["automatic"]:
            return "BLOCK_AUTOMATIC_DELETION_UNPROVEN"
        return "PASS" if case["max_months"] <= 6 else "BLOCK_EXCEEDS_MAXIMUM"
    if q == "universal_claim":
        return "REJECT_MULTIPLE_SERVICE_ROUTES"
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({r["id"] for r in model["atomic_rules"]}) == 18
    assert len(model["evidence_model"]) == len({r["id"] for r in model["evidence_model"]}) == 13
    assert model["sources"]["pp445"]["current_revision"] == "2022-03-28"
    assert model["sources"]["pp1066"]["effective_from"] == "2026-09-01"
    assert model["sources"]["pp1066"]["status_as_of_checked_at"] == "REGISTERED_NOT_YET_EFFECTIVE"
    assert model["temporal_model"][3]["initial_capacity_reference"] == "PRECEDING_30_DAYS_MESSAGE_VOLUME"
    assert model["temporal_model"][3]["annual_capacity_increase_percent"] == 15
    assert model["temporal_model"][3]["annual_increase_duration_years"] == 5
    assert model["verification_boundary"]["pp445_current_points_1_to_8"] == "VERIFIED_CURRENT_TEXT"
    assert model["verification_boundary"]["pp1066_official_pdf_bytes"] == "PENDING_TRANSIENT_FETCH_TIMEOUT"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 48

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 18 rules; 4 temporal routes; 13 evidence nodes; 48 cases; PP1066 pre-effective split preserved")


if __name__ == "__main__":
    main()
