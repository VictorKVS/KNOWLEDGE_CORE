#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-23-authorized-body-powers-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-23-authorized-body-powers-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")

COURT_ROUTES = {
    "SUBJECT_RIGHTS_CLAIM": "ALLOW_COURT_CLAIM",
    "INDEFINITE_PERSONS": "ALLOW_INDEFINITE_PERSONS_CLAIM",
    "SUBJECT_REPRESENTATION": "ALLOW_SUBJECT_REPRESENTATION",
    "REGULATOR_FINAL_JUDGMENT": "REJECT_COURT_DECIDES",
}


def evaluate(case):
    query = case["query"]
    if query == "authority":
        if not case["federal_executive"]:
            return "BLOCK_NOT_AUTHORIZED_BODY"
        return "PASS_AUTHORIZED_BODY" if case["independent_oversight"] else "BLOCK_FUNCTION_UNPROVEN"
    if query == "part1_1":
        return "REPEALED_DO_NOT_EXECUTE" if date.fromisoformat(case["as_of"]) >= date(2021, 7, 1) else "HISTORICAL_VERSION_REVIEW"
    if query == "subject_appeal":
        if not case["subject_appeal"]:
            return "NO_PART2_TRIGGER"
        if not case["content_review"]:
            return "BLOCK_CONTENT_REVIEW_MISSING"
        if not case["methods_review"]:
            return "BLOCK_METHODS_REVIEW_MISSING"
        return "PASS" if case["decision"] else "BLOCK_DECISION_MISSING"
    if query == "info_request":
        if not case["necessary"]:
            return "BLOCK_NECESSITY_UNPROVEN"
        return "BLOCK_INFORMATION_MUST_BE_FREE" if case["charged_fee"] else "ALLOW_REQUEST_FREE_RECEIPT"
    if query == "info_request_deadline":
        return "NOT_STATED_ROUTE_TO_ARTICLE20_OR_OTHER_PROCEDURE"
    if query == "notification_verification":
        if case["verify_directly"]:
            return "ALLOW_DIRECT_VERIFICATION"
        if not case["other_body"]:
            return "BLOCK_NO_VERIFICATION_ROUTE"
        return "ALLOW_OTHER_BODY_WITHIN_POWERS" if case["within_other_body_powers"] else "BLOCK_OTHER_BODY_OUTSIDE_POWERS"
    if query == "remediation":
        if case["data_condition"] not in {"INACCURATE", "UNLAWFULLY_OBTAINED"}:
            return "BLOCK_POINT3_CONDITION_MISSING"
        return {"CLARIFY": "ALLOW_REQUIRE_CLARIFICATION", "BLOCK": "ALLOW_REQUIRE_BLOCKING", "DESTROY": "ALLOW_REQUIRE_DESTRUCTION"}.get(case["action"], "BLOCK_NOT_POINT3_ACTION")
    if query == "access_restriction":
        if not case["violation"]:
            return "BLOCK_VIOLATION_UNPROVEN"
        return "ALLOW_RESTRICTION" if case["procedure_followed"] else "BLOCK_PROCEDURE_UNPROVEN"
    if query == "processing_measures":
        if not case["violation_152_fz"]:
            return "BLOCK_VIOLATION_UNPROVEN"
        if not case["procedure_followed"]:
            return "BLOCK_PROCEDURE_UNPROVEN"
        return "ALLOW_SUSPENSION_MEASURES" if case["action"] == "SUSPEND" else "ALLOW_TERMINATION_MEASURES"
    if query == "court":
        return COURT_ROUTES[case["route"]]
    if query == "article22_info":
        if case["field"] != "PART3_POINT7":
            return "BLOCK_ONLY_POINT7_ROUTE"
        if case["recipient"] not in {"FSB", "FSTEC"}:
            return "BLOCK_RECIPIENT_NOT_LISTED"
        return "ALLOW_TRANSFER" if case["sphere_relevant"] else "BLOCK_SPHERE_RELEVANCE_UNPROVEN"
    if query == "licensing":
        if case["action"] != "APPLY_TO_LICENSING_BODY":
            return "REJECT_LICENSING_BODY_DECIDES"
        return "ALLOW_APPLICATION" if case["licence_prohibits_transfer_without_written_consent"] else "BLOCK_LICENCE_CONDITION_MISSING"
    if query == "criminal_referral":
        if not case["crime_signs"]:
            return "BLOCK_CRIME_SIGNS_UNPROVEN"
        return "ALLOW_MATERIAL_REFERRAL" if case["jurisdiction_routed"] else "BLOCK_JURISDICTION_ROUTING_MISSING"
    if query == "criminal_referral_result":
        return "LAW_ENFORCEMENT_DECIDES_CASE_INITIATION"
    if query == "government_proposal":
        return "ALLOW_PROPOSAL" if case["topic"] in {"SUBJECT_RIGHTS_PROTECTION", "PROCESSING_ACTIVITY"} else "NO_POINT8_ROUTE"
    if query == "administrative":
        if not case["violation_152_fz"]:
            return "BLOCK_VIOLATION_UNPROVEN"
        return "ALLOW_ADMINISTRATIVE_LIABILITY" if case["procedure_followed"] else "BLOCK_PROCEDURE_UNPROVEN"
    if query == "confidentiality":
        if not case["personal_data_learned_in_activity"]:
            return "OUTSIDE_PART4_FACT_PATTERN"
        return "PASS" if case["protected"] else "BLOCK_CONFIDENTIALITY_BREACH"
    if query == "complaint":
        if not case["processing_issue"]:
            return "ROUTE_OUTSIDE_POINT2_PROCESSING_ISSUE"
        return "PASS_REVIEW_AND_DECISION" if case["decision_within_powers"] else "BLOCK_DECISION_OUTSIDE_POWERS"
    if query == "register":
        return "PASS_OPERATOR_REGISTER" if case["maintained"] else "BLOCK_OPERATOR_REGISTER_DUTY"
    if query == "security_submission":
        if case["submitter"] not in {"FSB", "FSO", "FSTEC"}:
            return "BLOCK_SUBMITTER_NOT_LISTED"
        return "ALLOW_MEASURES" if case["procedure_followed"] else "BLOCK_PROCEDURE_UNPROVEN"
    if query == "inform":
        if case["recipient"] == "DATA_SUBJECT" and not case["request_received"]:
            return "NO_POINT6_SUBJECT_TRIGGER"
        return "INFORM_RIGHTS_PROTECTION_STATE"
    if query == "other_duty":
        return "ALLOW_OTHER_STATUTORY_DUTY" if case["legal_basis"] else "BLOCK_SELF_CREATED_DUTY"
    if query == "foreign_cooperation":
        return "REJECT_NOT_CROSS_BORDER_PERMISSION" if case["action"] == "AUTHORIZE_OPERATOR_TRANSFER" else "ALLOW"
    if query == "adequate_list":
        return "PASS" if case["authority_approves"] else "BLOCK_WRONG_APPROVER"
    if query == "delegation":
        if case["part"] == "PART5_SUPPORT":
            return "NO_PART5_2_CLAIM_REVIEW_OTHER_LAW"
        return "BLOCK_NON_DELEGABLE" if case["delegated"] else "PASS_DIRECT_EXERCISE"
    if query == "judicial_appeal":
        return "REJECT_AUTOMATIC_STAY_NOT_STATED" if case["automatic_stay_claimed"] else "ALLOW_JUDICIAL_APPEAL"
    if query == "annual_report":
        if set(case["sent_to"]) != {"PRESIDENT", "GOVERNMENT", "FEDERAL_ASSEMBLY"}:
            return "BLOCK_RECIPIENT_SET_INCOMPLETE"
        return "PASS" if case["media_published"] else "BLOCK_MEDIA_PUBLICATION_MISSING"
    if query == "annual_report_due_date":
        return "ANNUAL_NO_EXACT_DATE_STATED"
    if query == "council":
        if not case["public_basis"]:
            return "BLOCK_PUBLIC_BASIS_MISSING"
        if not case["formation_rules"]:
            return "BLOCK_FORMATION_RULES_MISSING"
        return "PASS" if case["activity_rules"] else "BLOCK_ACTIVITY_RULES_MISSING"
    if query == "incident_register":
        if not case["article21_part3_1_incident"]:
            return "OUTSIDE_PART10_REGISTER_SCOPE"
        if not case["procedure_defined"]:
            return "BLOCK_PROCEDURE_MISSING"
        return "PASS_REGISTER_ROUTE" if case["conditions_defined"] else "BLOCK_CONDITIONS_MISSING"
    if query == "incident_transfer":
        if not case["covered_incident"]:
            return "NO_PART11_TRANSFER_TRIGGER"
        return "TRANSFER_TO_FSB" if case["joint_procedure"] else "BLOCK_JOINT_PROCEDURE_UNPROVEN"
    if query == "anonymization":
        if date.fromisoformat(case["as_of"]) < date(2025, 9, 1):
            return "PART12_NOT_YET_EFFECTIVE"
        return "EXCLUDED_ROUTE_TO_SPECIAL_REGIME" if case["article6_point9_1"] else "ROUTE_GENERAL_RKN_REQUIREMENTS_METHODS"
    if query == "numeric_deadline":
        return "NONE_IN_ARTICLE23"
    if query == "article23_1":
        return "SEPARATE_CONTROL_SUPERVISION_PROCEDURE"
    if query == "budget":
        return "PASS" if case["source"] == "FEDERAL_BUDGET" else "BLOCK_WRONG_BUDGET_SOURCE"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 61
    assert model["numeric_deadlines"] == []
    assert len(model["event_deadlines_without_numeric_value"]) == 5
    assert len(model["temporal_model"]) == 7
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 30
    assert len(model["conflict_and_definition_checks"]) == 30
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["source"]["official_266_fz_publication"]["publication_number"] == "0001202207140080"
    assert model["source"]["official_233_fz_publication"]["publication_number"] == "0001202408080031"
    assert model["verification_boundary"]["article_23_1_control_procedure_crosswalk"] == "PENDING"
    assert model["verification_boundary"]["incident_exchange_joint_procedure_current_clause_map"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0001")
    assert source["state"] == "ATOMIZED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-23")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
    assert len(fixtures["cases"]) == 100

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 61 atomic rules; 0 numeric deadlines; 5 event deadlines; 30 evidence nodes; 30 conflict checks; 100 cases")


if __name__ == "__main__":
    main()
