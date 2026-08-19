#!/usr/bin/env python3
import json
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-14-subject-access-rights-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-14-subject-access-rights-regression-v1.json")
ARTICLE20 = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-20-subject-regulator-requests-atomic-v1.yaml")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")

PART7_FIELDS = {
    "PROCESSING_CONFIRMATION",
    "LEGAL_BASES_AND_PURPOSES",
    "PURPOSES_AND_METHODS",
    "OPERATOR_AND_ACCESS_RECIPIENTS",
    "SUBJECT_DATA_AND_SOURCE",
    "PROCESSING_AND_STORAGE_PERIODS",
    "RIGHTS_EXERCISE_PROCEDURE",
    "CROSS_BORDER_TRANSFER",
    "PROCESSOR_IDENTITY_AND_ADDRESS",
    "ARTICLE18_1_COMPLIANCE_METHODS",
    "OTHER_STATUTORY_INFORMATION",
}


def evaluate(case):
    query = case["query"]
    if query == "request_validation":
        if not case["doc_number"]:
            return "BLOCK_ID_DOCUMENT_NUMBER_REQUIRED"
        if not case["issue_date"] or not case["issuer"]:
            return "BLOCK_ID_DOCUMENT_ISSUANCE_DETAILS_REQUIRED"
        if not case["processing_proof"]:
            return "BLOCK_RELATIONSHIP_OR_PROCESSING_PROOF_REQUIRED"
        if not case["signature"]:
            return "BLOCK_SIGNATURE_REQUIRED"
        if case["electronic"]:
            return "PASS_ELECTRONIC_REQUEST" if case["esign"] else "BLOCK_COMPLIANT_ELECTRONIC_SIGNATURE_REQUIRED"
        return "PASS"
    if query == "response_timing":
        if not case["delivered"]:
            return "BLOCK_PART7_INFORMATION_REQUIRED"
        if case["working_days"] <= 10:
            return "PASS"
        if not case["notice"]:
            return "BLOCK_REASONED_EXTENSION_NOTICE_REQUIRED"
        if not case["reasons"]:
            return "BLOCK_EXTENSION_REASONS_REQUIRED"
        return "PASS_EXTENDED" if case["working_days"] <= 15 else "BLOCK_MAXIMUM_EXTENSION_BREACHED"
    if query == "response_fields":
        required = PART7_FIELDS.copy()
        if not case["processor_used"]:
            required.remove("PROCESSOR_IDENTITY_AND_ADDRESS")
        missing = required - set(case["fields"])
        return "PASS" if not missing else f"BLOCK_MISSING_{sorted(missing)[0]}"
    if query == "repeat_request":
        allowed = case["days"] >= 30
        early_allowed = not case["complete_first_response"] and case["justification"] and case["request_fields"]
        if allowed:
            return "BLOCK_REFUSAL_NOT_JUSTIFIED_REPEAT_ALLOWED" if case["refused"] else "PASS_REPEAT_ALLOWED"
        if case["override"]:
            return "PASS_SHORTER_PERIOD_OVERRIDE"
        if early_allowed:
            return "BLOCK_REFUSAL_NOT_JUSTIFIED_EARLY_REPEAT_ALLOWED" if case["refused"] else "PASS_EARLY_REPEAT_INCOMPLETE_FIRST_RESPONSE"
        if not case["refused"]:
            return "BLOCK_NONCONFORMING_REPEAT_MAY_BE_REFUSED"
        if not case["reasoned"]:
            return "BLOCK_REFUSAL_MUST_BE_REASONED"
        return "PASS_REASONED_REFUSAL" if case["proof"] else "BLOCK_OPERATOR_PROOF_REQUIRED"
    if query == "access_restriction":
        if case["basis"] == "NONE":
            return "PROVIDE_ACCESS"
        if not case["federal_law"]:
            return "BLOCK_FEDERAL_LAW_BASIS_REQUIRED"
        if case["basis"] == "CRIMINAL_PROCEEDINGS" and case["criminal_exception"]:
            return "DO_NOT_LIMIT_WHERE_CRIMINAL_PROCEDURE_ALLOWS_INSPECTION"
        if case["basis"] == "THIRD_PARTY_RIGHTS" and case["rights_violation"]:
            return "ROUTE_TO_THIRD_PARTY_RIGHTS_LIMITATION"
        if case["basis"] == "OTHER_FEDERAL_LAW":
            return "ROUTE_TO_OTHER_FEDERAL_LAW_LIMITATION"
        return "ROUTE_TO_FEDERAL_LAW_LIMITATION"
    if query == "remediation_demand":
        if case["condition"] in {"INCOMPLETE", "OUTDATED", "INACCURATE"}:
            return "ROUTE_TO_CLARIFICATION"
        if case["condition"] in {"UNLAWFULLY_OBTAINED", "UNNECESSARY_FOR_PURPOSE"}:
            return "ROUTE_TO_BLOCKING_OR_DESTRUCTION"
        return "NO_ARTICLE14_REMEDIATION_TRIGGER_ESTABLISHED"
    if query == "response_form":
        if not case["accessible"]:
            return "BLOCK_ACCESSIBLE_FORM_REQUIRED"
        if case["other_subject_data"]:
            return "PASS_LAWFUL_OTHER_SUBJECT_DISCLOSURE" if case["lawful_disclosure"] else "BLOCK_OTHER_SUBJECT_DATA_MUST_BE_EXCLUDED"
        if not case["same_or_requested_form"]:
            return "BLOCK_RESPONSE_FORM_MISMATCH"
        return "PASS"
    if query == "deadline_unit":
        return "DAYS_NOT_WORKING_DAYS" if case["deadline"] == "REPEAT_FLOOR" else "WORKING_DAYS"
    if query == "part8_scope":
        return "NON_EXHAUSTIVE_FEDERAL_LAW_LIMITATIONS"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    article20 = yaml.safe_load(ARTICLE20.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 37
    assert len(model["deadlines"]) == len({item["id"] for item in model["deadlines"]}) == 3
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 17
    assert len(model["conflict_and_definition_checks"]) == 12
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["source"]["reform_law"]["official_publication"]["number"] == "0001202207140080"
    assert model["source"]["execution_dependency"] == article20["id"]
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(item for item in library["sources"] if item["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-11")
    assert direction["maturity"] == "EXECUTABLE"
    assert len(fixtures["cases"]) == 56
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 37 atomic rules; 3 deadlines; 4 temporal events; 17 evidence nodes; 12 conflict checks; 56 cases")


if __name__ == "__main__":
    main()
