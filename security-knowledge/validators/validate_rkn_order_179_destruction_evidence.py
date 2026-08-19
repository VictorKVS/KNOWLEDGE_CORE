#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/rkn-order-179-destruction-evidence-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/rkn-order-179-destruction-evidence-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "validity":
        as_of = date.fromisoformat(case["as_of"])
        if as_of < date(2023, 3, 1):
            return "NOT_YET_EFFECTIVE"
        if as_of >= date(2029, 3, 1):
            return "SUNSET_REACHED_REQUIRE_SUCCESSOR_OR_EXTENSION"
        return "CURRENT_SUBJECT_TO_VERSION_CHECK"
    if query == "document_set":
        mode, act, log = case["mode"], case["act"], case["log_extract"]
        if mode == "NON_AUTOMATED":
            return "PASS_ACT" if act else "BLOCK_ACT_REQUIRED"
        if mode in {"AUTOMATED", "MIXED"}:
            return "PASS_ACT_AND_LOG" if act and log else "BLOCK_ACT_AND_LOG_REQUIRED"
        return "BLOCK_MODE_CLASSIFICATION_REQUIRED"
    if query == "act":
        checks = [
            ("operator_identity_address", "BLOCK_OPERATOR_IDENTITY_OR_ADDRESS_MISSING"),
            ("processor_identity_address_if_delegated", "BLOCK_PROCESSOR_IDENTITY_OR_ADDRESS_MISSING"),
            ("subject_identifier", "BLOCK_SUBJECT_IDENTIFIER_MISSING"),
            ("destroyer_identity_position_signature", "BLOCK_DESTROYER_IDENTITY_POSITION_OR_SIGNATURE_MISSING"),
            ("categories", "BLOCK_CATEGORIES_MISSING"),
            ("mode_specific_carrier_or_ispdn", "BLOCK_MODE_SPECIFIC_CARRIER_OR_ISPDN_MISSING"),
            ("method", "BLOCK_METHOD_MISSING"),
            ("reason", "BLOCK_REASON_MISSING"),
            ("date", "BLOCK_DATE_MISSING"),
        ]
        for field, result in checks:
            if not case[field]:
                return result
        return "PASS"
    if query == "processor_field":
        if not case["delegated"]:
            return "NOT_APPLICABLE"
        return "PASS" if case["processor_identity_address"] else "BLOCK_PROCESSOR_IDENTITY_OR_ADDRESS_MISSING"
    if query == "electronic_act":
        return "EQUIVALENT_TO_SIGNED_PAPER_ACT" if case["signed_under_63_fz"] else "NOT_EQUIVALENT_SIGNATURE_REQUIREMENT_UNPROVEN"
    if query == "log_extract":
        checks = [
            ("subject_identifier", "BLOCK_OR_ROUTE_MISSING_SUBJECT_IDENTIFIER_TO_ACT"),
            ("categories", "BLOCK_OR_ROUTE_MISSING_CATEGORIES_TO_ACT"),
            ("ispdn", "BLOCK_OR_ROUTE_MISSING_ISPDN_TO_ACT"),
            ("reason", "BLOCK_OR_ROUTE_MISSING_REASON_TO_ACT"),
            ("date", "BLOCK_OR_ROUTE_MISSING_DATE_TO_ACT"),
        ]
        for field, result in checks:
            if not case[field]:
                return result
        return "PASS"
    if query == "log_gap":
        if case["log_can_contain"]:
            return "BLOCK_FIELD_MUST_REMAIN_IN_LOG"
        return "PASS_MISSING_LOG_FIELD_RELOCATED_TO_ACT" if case["field_present_in_act"] else "BLOCK_FIELD_MUST_BE_IN_ACT"
    if query == "conditional_act_fields":
        mode = case["mode"]
        media, ispdn = case["material_media_with_sheet_counts"], case["ispdn_names"]
        if mode == "NON_AUTOMATED":
            return "PASS" if media else "BLOCK_PHYSICAL_MEDIA_AND_SHEET_COUNTS_REQUIRED"
        if mode == "AUTOMATED":
            return "PASS" if ispdn else "BLOCK_ISPDN_NAMES_REQUIRED"
        if mode == "MIXED":
            return "PASS" if media and ispdn else "BLOCK_BOTH_MODE_SPECIFIC_FIELD_GROUPS_REQUIRED"
        return "BLOCK_MODE_CLASSIFICATION_REQUIRED"
    if query == "retention":
        return "RETAIN_EVIDENCE_PACKAGE" if case["elapsed_years"] < 3 else "THREE_YEAR_MINIMUM_SATISFIED_SUBJECT_TO_OTHER_RETENTION_RULES"
    if query == "retention_scope":
        return "REJECT_RETENTION_APPLIES_TO_ACT_AND_LOG_ONLY"
    if query == "destruction_deadline":
        return "NOT_STATED_ROUTE_TO_152_FZ_ARTICLE_21"
    if query == "destruction_method":
        return "NOT_PRESCRIBED_RECORD_ACTUAL_METHOD"
    if query == "legal_trigger":
        return "REJECT_ORDER_CONFIRMS_ARTICLE_21_DESTRUCTION"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 22
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 14
    assert len(model["conflict_and_definition_checks"]) == 7
    assert model["source"]["official_publication"]["number"] == "0001202211290008"
    assert model["source"]["minjust_registration"]["number"] == "71167"
    assert model["source"]["effective_from"] == "2023-03-01"
    assert model["source"]["valid_until_exclusive"] == "2029-03-01"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0014")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-22")
    assert direction["maturity"] == "EXECUTABLE"
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
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
    print("PASS: 22 atomic rules; 4 temporal events; 14 evidence nodes; 7 conflict checks; 44 cases")


if __name__ == "__main__":
    main()
