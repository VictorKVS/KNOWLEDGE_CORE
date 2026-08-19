#!/usr/bin/env python3
import json
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-20-subject-regulator-requests-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-20-subject-regulator-requests-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def extended(case, base=10):
    days = case["working_days"]
    if days <= base:
        return None
    if not case["notice"]:
        return "BLOCK_REASONED_EXTENSION_NOTICE_REQUIRED"
    if not case["reasons"]:
        return "BLOCK_EXTENSION_REASONS_REQUIRED"
    return "PASS_EXTENDED" if days <= base + 5 else "BLOCK_MAXIMUM_EXTENSION_BREACHED"


def evaluate(case):
    q = case["query"]
    if q == "subject_access":
        if case["route"] == "EMAIL_WITHOUT_VALID_REQUEST":
            return "ROUTE_TO_ARTICLE14_REQUEST_VALIDATION"
        if case["route"] == "APPEAL":
            return "PASS_AT_APPEAL" if case["delivered"] and case["at_appeal"] else "BLOCK_APPEAL_ROUTE_NOT_SATISFIED"
        if case["working_days"] > 10:
            return "BLOCK_TEN_WORKING_DAY_DEADLINE_BREACHED"
        return "PASS" if case["delivered"] else "BLOCK_INFORMATION_AND_INSPECTION_REQUIRED"
    if q == "subject_extension":
        if case["working_days"] <= 10:
            return "PASS_BASE_PERIOD"
        return extended(case)
    if q == "refusal":
        if not case["written"]:
            return "BLOCK_WRITTEN_RESPONSE_REQUIRED"
        if not case["reasoned"]:
            return "BLOCK_REASONING_REQUIRED"
        if case["legal_locator"] not in {"ARTICLE14_PART8", "OTHER_FEDERAL_LAW"}:
            return "BLOCK_FEDERAL_LAW_LOCATOR_REQUIRED"
        if case["working_days"] <= 10:
            return "PASS"
        return extended({"working_days": case["working_days"], "notice": case["notice"], "reasons": case["extension_reasons"]})
    if q in {"correction", "destruction"}:
        if not case["evidence"]:
            return "NO_CORRECTION_TRIGGER_ESTABLISHED" if q == "correction" else "NO_DESTRUCTION_TRIGGER_ESTABLISHED"
        if case["working_days"] > 7:
            return "BLOCK_SEVEN_WORKING_DAY_DEADLINE_BREACHED"
        complete = case["changed"] if q == "correction" else case["destroyed"]
        return "PASS" if complete else ("BLOCK_CORRECTION_REQUIRED" if q == "correction" else "BLOCK_DESTRUCTION_REQUIRED")
    if q == "notifications":
        if not case["subject_notified"]:
            return "BLOCK_SUBJECT_RESULT_NOTICE_REQUIRED"
        if case["third_party_transfers"] and not case["reasonable_measures"]:
            return "BLOCK_REASONABLE_THIRD_PARTY_NOTICE_MEASURES_REQUIRED"
        return "PASS" if case["third_party_transfers"] else "PASS_NO_TRANSFERRED_THIRD_PARTIES"
    if q == "notification_deadline":
        return "NOT_STATED_DO_NOT_INVENT"
    if q == "regulator":
        if not case["provided"]:
            return "BLOCK_NECESSARY_INFORMATION_REQUIRED"
        if case["working_days"] <= 10:
            return "PASS"
        return extended(case)
    if q == "free_access":
        return "PASS_FREE_ACCESS" if case["fee"] == 0 else "BLOCK_FEE_NOT_AUTHORIZED"
    if q == "deadline_unit":
        return "WORKING_DAYS_NOT_CALENDAR_DAYS"
    if q == "article14_dependency":
        return "ROUTE_TO_SEPARATE_ARTICLE14_MODEL"
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 15
    assert len(model["deadlines"]) == len({x["id"] for x in model["deadlines"]}) == 8
    assert len(model["event_deadlines_without_numeric_value"]) == 3
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 12
    assert len(model["conflict_and_definition_checks"]) == 10
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["source"]["reform_law"]["official_publication"]["number"] == "0001202207140080"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(x for x in library["sources"] if x["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(x for x in matrix["directions"] if x["id"] == "PDN-DIR-11")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert len(fixtures["cases"]) == 44
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 15 atomic rules; 8 numeric deadlines; 3 event deadlines; 12 evidence nodes; 10 conflict checks; 44 cases")


if __name__ == "__main__":
    main()
