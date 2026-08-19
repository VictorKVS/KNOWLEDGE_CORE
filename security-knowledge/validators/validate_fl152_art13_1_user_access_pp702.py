#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-art13-1-user-access-pp702-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-art13-1-user-access-pp702-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "user_class":
        return "PUBLIC_USER_ROUTE_NO_PP702_CHECK" if case["type"] == "STATE_BODY" else "PRIVATE_USER_PP702_CHECK_REQUIRED"
    if query == "private_eligibility":
        return "PASS_STATUTORY_CRITERIA_CONTINUE_PP702" if case["operator_register"] else "BLOCK_OPERATOR_REGISTER"
    if query == "legal_control":
        return "PASS_CONTROL_THRESHOLD" if case["voting_percent"] > 50 else "BLOCK_NOT_MORE_THAN_50_PERCENT"
    if query == "legal_reliability":
        return "BLOCK_EGRUL_UNRELIABLE" if case["egrul_unreliable_record"] else "PASS_RELIABILITY_GATE"
    if query == "list_screening":
        return "BLOCK_LIST_SCREENING" if case["listed_person_or_entity"] else "PASS_LIST_GATE"
    if query == "foreign_citizenship":
        return "BLOCK_FOREIGN_CITIZENSHIP" if case["has_foreign_citizenship"] else "PASS_CITIZENSHIP_GATE"
    if query == "conviction":
        return "BLOCK_CONVICTION" if case["unexpunged_or_outstanding"] else "PASS_CONVICTION_GATE"
    if query == "five_year_liability":
        if case["specific_articles"] or not case["exact_dates_proven"]:
            return "BLOCK_PENDING_EXACT_DATE_AND_STATUS"
        return "PASS_FIVE_YEAR_TEST"
    if query == "part9":
        triggered = case["source_operator"] == "PRIVATE" and case["data_recent_within_3_years"]
        if not triggered:
            return "NO_PART9_EMBARGO_CONTINUE_OTHER_GATES"
        if case["user_class"] == "PRIVATE" and case["years_since_gis_provision"] < 1:
            return "BLOCK_PRIVATE_USER_ONE_YEAR_EMBARGO"
        return "CONTINUE_OTHER_ACCESS_GATES"
    if query == "part9_anchor":
        return "SOURCE_DATA_PROVISION_TO_GIS_FOR_BOTH_CLOCKS"
    if query == "processing_location":
        return "ALLOW_SUBJECT_TO_OTHER_GATES" if case["inside_designated_gis"] else "BLOCK_OUTSIDE_GIS"
    if query == "dataset_export":
        return "BLOCK_EXPORT_ACTION"
    if query == "protected_harm":
        return "BLOCK_PROCESSING_AND_RESULTS"
    if query == "defense_security_result":
        return "BLOCK_RESULT_PROVISION" if case["fsb_prohibition"] else "CONTINUE_OTHER_GATES"
    if query == "foreign_result":
        return "CONTINUE_OTHER_GATES" if case["exception_basis"] else "BLOCK_FOREIGN_RESULT"
    if query == "pp702_request":
        return "ACCEPT_FOR_CHECK" if case["complete"] and case["signature_valid"] else "CLARIFICATION_OR_REFUSAL_ROUTE"
    if query == "initial_check_deadline":
        return "15_WORKING_DAYS_FROM_REQUEST_RECEIPT"
    if query == "clarification":
        return "WAIT_FOR_RESPONSE" if case["response_within_15_working_days"] else "SIGNED_REASONED_REFUSAL"
    if query == "annual_reverification":
        return "RECHECK_UNDER_PP702_7_TO_10" if case["fresh_request_before_anniversary"] else "SUSPEND_SYSTEM_ACCESS"
    if query == "change_notice_deadline":
        return "5_WORKING_DAYS_FROM_AWARENESS"
    if query == "post_change_nonconformity":
        return "REASONED_REFUSAL_WITHIN_3_WORKING_DAYS_AND_ROUTE_PP961_BLOCK"
    if query == "interagency_response":
        return "5_WORKING_DAYS_UNLESS_OTHER_LAW"
    if query == "clock_collision":
        return "ONE_YEAR_FROM_CONFORMITY_NOTICE_NOT_PART9_EMBARGO"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))

    assert len(model["statutory_user_classes"]) == 2
    assert len(model["private_user_eligibility_criteria"]) == 7
    assert len({row["id"] for row in model["private_user_eligibility_criteria"]}) == 7
    assert len(model["article_13_1_access_and_use_rules"]) == 5
    assert len(model["pp702_workflow_rules"]) == 16
    assert len({row["id"] for row in model["pp702_workflow_rules"]}) == 16
    assert [(row["value"], row["unit"]) for row in model["deadlines"]] == [
        (15, "WORKING_DAYS"),
        (15, "WORKING_DAYS"),
        (1, "YEAR"),
        (5, "WORKING_DAYS"),
        (3, "WORKING_DAYS"),
        (5, "WORKING_DAYS"),
    ]
    assert len(model["evidence_model"]) == 14
    assert model["decree_702_source"]["official_publication"]["publication_number"] == "0001202505280017"
    assert str(model["decree_702_source"]["effective_from"]["date"]) == "2025-09-01"
    assert model["verification_boundary"]["immutable_official_pdf_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0034")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"]
    assert str(FIXTURES) in source["repo_bindings"]
    assert library["counts"]["registered_source_records"] == len(library["sources"])
    assert len(fixtures["cases"]) == 36

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 7 eligibility criteria; 5 access/use rules; 16 PP702 rules; 6 clocks; 36 cases")


if __name__ == "__main__":
    main()
