#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/pp-rf-211-state-municipal-operators-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/pp-rf-211-state-municipal-operators-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "scope":
        return "PP211_APPLIES" if case["state_or_municipal_body_operator"] else "PP211_NOT_APPLICABLE"
    if query == "scope_private_processor":
        return "DO_NOT_APPLY_WITHOUT_OPERATOR_STATUS"
    if query == "appointment":
        eligible = {
            "STATE_OR_MUNICIPAL_SERVANT",
            "NON_CIVIL_SERVICE_EMPLOYEE_UNDER_EMPLOYMENT_CONTRACT",
        }
        return "ELIGIBLE" if case["candidate_status"] in eligible else "BLOCK_NOT_IN_STATED_POOL"
    if query == "appointment_historical":
        if date.fromisoformat(case["as_of"]) < date(2019, 4, 25):
            return "REJECT_UNDER_PRE_PP454_TEXT"
        return "ELIGIBLE_UNDER_PP454"
    if query == "document_set":
        if not case["head_approval_act"]:
            return "BLOCK_HEAD_APPROVAL_ACT_MISSING"
        return "PASS" if case["all_unconditional_documents"] else "BLOCK_DOCUMENT_SET_INCOMPLETE"
    if query == "anonymization_documents":
        if not case["anonymization_performed"]:
            return "CONDITIONAL_DOCUMENTS_NOT_TRIGGERED"
        if not case["rules_present"]:
            return "BLOCK_ANONYMIZED_DATA_RULES_MISSING"
        return "PASS" if case["position_list_present"] else "BLOCK_ANONYMIZATION_POSITION_LIST_MISSING"
    if query == "consent_form":
        return "PASS_FORM_CONTROL" if case["consent_is_applicable_basis"] else "FORM_DOES_NOT_CREATE_UNIVERSAL_CONSENT_BASIS"
    if query == "ispdn_security":
        return "PASS" if case["applicable_security_crosswalk_complete"] else "BLOCK_APPLICABLE_SECURITY_MEASURES_UNPROVEN"
    if query == "ispdn_security_source":
        return "REJECT_PP211_IS_CROSS_REFERENCE_NOT_REPLACEMENT"
    if query == "non_automated":
        return "PASS" if case["pp687_crosswalk"] else "BLOCK_PP687_COMPLIANCE_UNPROVEN"
    if query == "non_automated_legal_basis":
        return "REJECT_NO_PROCESSING_BASIS_CREATED"
    if query == "inspection":
        if not case["periodic_inspections"]:
            return "BLOCK_PERIODIC_INSPECTIONS_MISSING"
        if not case["authorized_checker"]:
            return "BLOCK_CHECKER_ROLE_NOT_AUTHORIZED"
        return "PASS" if case["report_to_head"] else "BLOCK_RESULT_AND_REMEDIATION_REPORT_MISSING"
    if query == "inspection_interval":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "awareness":
        return "PASS" if case["direct_processors_familiarized_or_trained"] else "BLOCK_AWARENESS_OR_TRAINING_EVIDENCE_MISSING"
    if query == "notification":
        if case["statutory_exception_applies"]:
            return "EXCEPTION_MEMO_REQUIRED_NOT_UNIVERSAL_NOTIFICATION"
        return "PASS" if case["notification_receipt"] else "BLOCK_NOTIFICATION_EVIDENCE_MISSING"
    if query == "anonymization_trigger":
        if not case["npa_case_established"]:
            return "PP211_DOES_NOT_ITSELF_TRIGGER_ANONYMIZATION"
        return "PASS" if case["authorized_requirements_and_methods_used"] else "BLOCK_AUTHORIZED_METHOD_UNPROVEN"
    if query == "publication":
        if not case["covered_policy_document"]:
            return "PP211_TEN_DAY_CLOCK_NOT_PROVEN_FOR_THIS_DOCUMENT"
        if case["days_after_approval"] > 10 or not case["official_site"]:
            return "BLOCK_TEN_DAY_CLOCK_BREACHED"
        return "PASS"
    if query == "role_collision":
        return "BLOCK_ROLE_COLLAPSE_NOT_CREATED_BY_PP211" if not case["separate_authority_and_sod_review"] else "PASS"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 24
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 20
    assert len(model["conflict_and_definition_checks"]) == 6
    assert model["source"]["current_edition"] == "2019-04-15"
    assert model["source"]["current_edition_effective_from"] == "2019-04-25"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0004")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-28")
    assert direction["maturity"] == "SUBSTANTIAL_ATOMIC"
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
    assert len(fixtures["cases"]) == 38

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 24 atomic rules; 4 temporal events; 20 evidence nodes; 6 conflict checks; 38 cases")


if __name__ == "__main__":
    main()
