#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-18-collection-notice-localization-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-18-collection-notice-localization-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")

REQUIRED_NOTICE_FIELDS = [
    "operator_identity_address", "purpose_legal_basis", "personal_data_list",
    "intended_users", "subject_rights", "source",
]
PROHIBITED_OPERATIONS = {
    "RECORDING", "SYSTEMATIZATION", "ACCUMULATION", "STORAGE", "CLARIFICATION", "EXTRACTION",
}
EXACT_ARTICLE6_EXCEPTIONS = {"A6P1P2", "A6P1P3", "A6P1P4", "A6P1P8"}


def evaluate(case):
    query = case["query"]
    if query == "direct_request":
        if not case["collection_context"]:
            return "ARTICLE18_PART1_COLLECTION_CONTEXT_NOT_ESTABLISHED"
        if not case["subject_request"]:
            return "NO_ARTICLE18_PART1_REQUEST_TRIGGER"
        return "PASS_PROVIDE_COMPLETE_ART14_PART7_INFORMATION" if case["article14_part7_complete"] else "BLOCK_INCOMPLETE_ART14_PART7_INFORMATION"
    if query == "mandatory_explanation":
        data = case["federal_law_requires_data"]
        consent = case["federal_law_requires_consent"]
        if data and consent:
            return "EXPLAIN_DATA_AND_CONSENT_REFUSAL_LEGAL_CONSEQUENCES"
        if data:
            return "EXPLAIN_DATA_REFUSAL_LEGAL_CONSEQUENCES"
        if consent:
            return "EXPLAIN_CONSENT_REFUSAL_LEGAL_CONSEQUENCES"
        return "INTERNAL_POLICY_DOES_NOT_CREATE_PART2_TRIGGER" if case["internal_policy_only"] else "NO_ARTICLE18_PART2_FEDERAL_LAW_TRIGGER"
    if query == "indirect_notice":
        if case["collection_source"] == "SUBJECT":
            return "PART3_NOTICE_NOT_APPLICABLE_DIRECT_COLLECTION"
        if case["collection_source"] != "THIRD_PARTY":
            return "BLOCK_COLLECTION_SOURCE_NOT_ESTABLISHED"
        if case["part4_exception"]:
            return "ROUTE_TO_PART4_EXCEPTION_VALIDATION"
        return "PASS_INDIRECT_NOTICE_BEFORE_PROCESSING" if case["notice_before_processing"] else "BLOCK_INDIRECT_NOTICE_NOT_BEFORE_PROCESSING"
    if query == "notice_fields":
        fields = set(case["fields"])
        for field in REQUIRED_NOTICE_FIELDS:
            if field not in fields:
                return f"BLOCK_MISSING_{field.upper()}"
        return "PASS_ALL_SIX_PART3_INFORMATION_ELEMENTS"
    if query == "part4_exception":
        basis = case["basis"]
        conditions = case["conditions_met"]
        if basis == "ALREADY_NOTIFIED":
            return "PASS_ALREADY_NOTIFIED_EXCEPTION" if conditions else "BLOCK_ALREADY_NOTIFIED_NOT_PROVED"
        if basis == "FEDERAL_LAW":
            return "PASS_FEDERAL_LAW_SOURCE_EXCEPTION" if conditions else "BLOCK_FEDERAL_LAW_SOURCE_NOT_PROVED"
        if basis == "QUALIFYING_CONTRACT":
            return "PASS_QUALIFYING_CONTRACT_EXCEPTION" if conditions else "BLOCK_CONTRACT_ROLE_NOT_QUALIFYING"
        if basis == "UNRELATED_PARTIES_CONTRACT":
            return "BLOCK_CONTRACT_ROLE_NOT_QUALIFYING"
        if basis == "DISSEMINATION_DATA":
            return "PASS_ARTICLE10_1_COMPLIANT_EXCEPTION" if conditions else "BLOCK_ARTICLE10_1_CONDITIONS_NOT_MET"
        if basis == "STATISTICAL_RESEARCH":
            return "PASS_RESEARCH_RIGHTS_PROTECTED_EXCEPTION" if conditions else "BLOCK_SUBJECT_RIGHTS_CONDITION_FAILED"
        if basis == "JOURNALISM_CREATIVE":
            return "PASS_CREATIVE_RIGHTS_PROTECTED_EXCEPTION" if conditions else "BLOCK_SUBJECT_RIGHTS_CONDITION_FAILED"
        if basis == "THIRD_PARTY_RIGHTS":
            return "PASS_THIRD_PARTY_RIGHTS_EXCEPTION" if conditions else "BLOCK_THIRD_PARTY_RIGHTS_NOT_PROVED"
        return "BLOCK_UNSTATED_PART4_EXCEPTION"
    if query == "localization_operation":
        if case["citizenship"] == "UNKNOWN":
            return "BLOCK_CITIZENSHIP_NOT_ESTABLISHED"
        if case["citizenship"] != "RF":
            return "OUTSIDE_EXPRESS_RF_CITIZEN_SCOPE"
        if not case["collection_context"]:
            return "ARTICLE18_PART5_COLLECTION_CONTEXT_NOT_ESTABLISHED"
        if case["database_location"] == "UNKNOWN":
            return "BLOCK_DATABASE_LOCATION_NOT_ESTABLISHED"
        if case["database_location"] != "OUTSIDE_RF":
            return "PASS_DATABASE_NOT_OUTSIDE_RF"
        if case["operation"] not in PROHIBITED_OPERATIONS:
            return "ARTICLE18_PART5_OPERATION_NOT_ENUMERATED_CHECK_OTHER_LAW"
        exception = case["article6_exception"]
        if exception in EXACT_ARTICLE6_EXCEPTIONS:
            return "PASS_EXACT_ARTICLE6_LOCALIZATION_EXCEPTION"
        if exception:
            return "BLOCK_ARTICLE6_BASIS_NOT_ENUMERATED_EXCEPTION"
        return f"BLOCK_FOREIGN_DATABASE_{case['operation']}"
    if query == "effective_date":
        current = date.fromisoformat(case["event_date"])
        return "APPLY_CURRENT_PART5_PROHIBITION" if current >= date(2025, 7, 1) else "ROUTE_TO_PREVIOUS_PART5_EDITION"
    constants = {
        "deadline": "NO_NUMERIC_DEADLINE_STATED",
        "sanction": "NOT_CREATED_BY_ARTICLE18_CHECK_KOAP",
        "foreign_owner_rf_database": "FOREIGN_OWNERSHIP_ALONE_NOT_FOREIGN_DATABASE_LOCATION",
    }
    if query == "cross_border_relation":
        return {
            "COMPLIANT_RF_COLLECTION_THEN_FOREIGN_TRANSFER": "CHECK_ARTICLE12_SEPARATELY",
            "INITIAL_RECORDING_IN_FOREIGN_DATABASE": "CHECK_ARTICLE18_PART5_FIRST",
        }[case["scenario"]]
    if query in constants:
        return constants[query]
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 28
    assert model["numeric_deadlines"] == []
    assert len(model["event_deadlines_without_numeric_value"]) == 2
    assert len(model["temporal_model"]) == 8
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 18
    assert len(model["conflict_and_definition_checks"]) == 20
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["source"]["official_amendment_23_fz"]["effective_from"] == "2025-07-01"
    assert model["verification_boundary"]["immutable_current_consolidated_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(item for item in library["sources"] if item["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    localization = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-10")
    indirect = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-13")
    assert localization["maturity"] == "REGRESSION_PROTECTED"
    assert indirect["maturity"] == "REGRESSION_PROTECTED"
    assert len(fixtures["cases"]) == 64
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 28 atomic rules; 0 numeric deadlines; 2 event deadlines; 18 evidence nodes; 20 conflict checks; 64 cases")


if __name__ == "__main__":
    main()
