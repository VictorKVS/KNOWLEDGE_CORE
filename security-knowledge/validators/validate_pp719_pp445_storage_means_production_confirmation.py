#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/government-decrees/719/pp445-storage-means-production-confirmation-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/government-decrees/719/pp445-storage-means-production-confirmation-regression-v1.json")


def evaluate(case):
    q = case["query"]
    if q == "version":
        return "CURRENT_REGISTRY_RULES" if date.fromisoformat(case["as_of"]) >= date(2024, 7, 1) else "HISTORICAL_PRE_REGISTRY_RULES"
    if q == "pp1026":
        d = date.fromisoformat(case["as_of"])
        if d < date(2026, 8, 21):
            return "NOT_EFFECTIVE"
        return "POINTS1_TO6_CURRENT" if d >= date(2027, 1, 1) else "POINT1_ONLY_CURRENT"
    if q == "basis":
        if case["basis"] == "EXPERTISE_ACT" and case["product_in_appendix"]:
            return "ALLOW_BASIS"
        if case["basis"] == "ST1":
            return "BLOCK_WRONG_BASIS" if case["product_in_appendix"] else "ALLOW_BASIS"
        return "BLOCK_UNENUMERATED_BASIS"
    if q == "application":
        if not case["gisp"]:
            return "BLOCK_NOT_GISP"
        return "PASS" if case["qes"] else "BLOCK_QES_MISSING"
    if q == "catalog":
        return "PASS" if case["catalog_card"] else "BLOCK_CATALOG_CARD_MISSING"
    if q == "forwarding":
        return "PASS" if case["working_days"] <= 1 else "BLOCK_EXCEEDS_NEXT_WORKING_DAY"
    if q == "minprom_review":
        return "PASS" if case["working_days"] <= 10 else "BLOCK_EXCEEDS_TEN_WORKING_DAYS"
    if q == "correction":
        return "NO_CORRECTION_GROUND" if case["complete"] and case["consistent"] else "RETURN_FOR_CORRECTION"
    if q == "record_fields":
        for field, result in (("number", "BLOCK_RECORD_NUMBER_MISSING"), ("expires", "BLOCK_VALIDITY_MISSING"), ("product", "BLOCK_PRODUCT_MISSING"), ("codes", "BLOCK_CODES_MISSING")):
            if not case[field]:
                return result
        return "PASS"
    if q == "validity":
        if case["basis"] == "SPIC_OR_ST1":
            return "PASS" if case["years"] == 3 else "BLOCK_THREE_YEAR_ROUTE"
        if case["years"] > 5:
            return "BLOCK_FIVE_YEAR_CAP"
        return "PASS" if case["years"] <= case["document_period_years"] else "BLOCK_EXCEEDS_DOCUMENTED_PERIOD"
    if q == "record_status":
        if case["excluded"]:
            return "BLOCK_EXCLUDED"
        if case["expired"] or not case["active"]:
            return "BLOCK_EXPIRED"
        return "ACTIVE"
    if q == "annual_report":
        d = date.fromisoformat(case["submitted_date"])
        return "PASS" if (d.month, d.day) <= (4, 1) else "LATE"
    if q == "nonreporting":
        return "EXCLUSION_GROUND" if case["days_after_due"] >= 90 else "NOT_YET_EXCLUSION_GROUND"
    if q == "exclusion_notice":
        return "PASS" if case["working_days"] <= 5 else "BLOCK_EXCEEDS_FIVE_WORKING_DAYS"
    if q == "installation_match":
        if not case["active"]:
            return "BLOCK_INACTIVE_RECORD"
        if not case["product_match"]:
            return "BLOCK_PRODUCT_MISMATCH"
        if not case["codes_match"]:
            return "BLOCK_CODE_MISMATCH"
        return "PASS" if case["date_match"] else "BLOCK_DATE_MISMATCH"
    if q == "claim":
        return {
            "MANUFACTURER_LISTING_COVERS_ALL_PRODUCTS": "REJECT_PRODUCT_SPECIFIC_MATCH_REQUIRED",
            "PERMANENT_NUMBER_MEANS_PERMANENT_VALIDITY": "REJECT_ID_VALIDITY_CONFLATION",
            "EXPERTISE_ACT_ALONE_PROVES_PP445_COMPLIANCE": "REJECT_ACTIVE_RECORD_REQUIRED",
            "THREE_YEARS_FOR_ALL_RECORDS": "REJECT_BASIS_SPECIFIC_VALIDITY",
            "GISP_UNAVAILABLE_MEANS_PRODUCT_ABSENT": "REJECT_TRANSPORT_ABSENCE_INFERENCE",
        }[case["claim"]]
    if q == "product_specific":
        return "PASS" if case["section_ix_verified"] and case["live_record_verified"] else "PENDING_FAIL_CLOSED"
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({r["id"] for r in model["atomic_rules"]}) == 34
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({r["id"] for r in model["evidence_model"]}) == 16
    assert model["sources"]["pp1026"]["official_publication_date"] == "2026-08-21"
    assert model["sources"]["pp1026"]["amendment_points_2_to_6_effective_from"] == "2027-01-01"
    assert model["verification_boundary"]["current_pp719_general_registry_route"] == "VERIFIED"
    assert model["verification_boundary"]["section_ix_storage_system_exact_operations_points_and_thresholds"] == "VERIFIED_BY_LINKED_MODEL"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 52
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 34 rules; 4 temporal routes; 16 evidence nodes; 52 cases; PP719 registry route for PP445 preserved fail-closed")


if __name__ == "__main__":
    main()
