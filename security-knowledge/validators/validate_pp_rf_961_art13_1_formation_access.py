#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/pp-rf-961-2025-art13-1-formation-access-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/pp-rf-961-2025-art13-1-formation-access-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
REQUIRED_FIELDS = {"ACCESS_PURPOSE", "PLANNED_RESULT_OR_ITS_CONTENT", "DATASET_PROCESSING_PERIOD", "LEGAL_GROUNDS_FOR_ACCESS"}
THREATS = {"MEMBERSHIP_INFERENCE", "LINKAGE_OR_ENRICHMENT", "VALUE_INFERENCE"}


def evaluate(case):
    query = case["query"]
    if query == "formation_scope":
        if not case["operator_requirement"]:
            return "BLOCK_MISSING_OPERATOR_REQUIREMENT"
        return "ALLOW_FORMATION_WORKFLOW" if case["pp538_case"] else "BLOCK_MISSING_PP538_CASE"
    if query == "formation_deadline":
        return "30_WORKING_DAYS_FROM_OPERATOR_DATA_RECEIPT"
    if query == "security_response_deadline":
        return "10_CALENDAR_DAYS_FROM_SECURITY_REQUEST" if case["security_request_received"] else "NO_CLOCK_WITHOUT_SECURITY_REQUEST"
    if query == "formation_threats":
        return "PASS_ALL_THREE" if set(case["considered"]) == THREATS else "BLOCK_INCOMPLETE_THREAT_SET"
    if query == "data_category_gate":
        if case["biometric"]:
            return "BLOCK_BIOMETRIC"
        if case["article10_special"] and not case["article10_part2_1"]:
            return "BLOCK_SPECIAL_CATEGORY"
        return "ALLOW_CATEGORY_GATE_REVIEW"
    if query == "access_request_fields":
        return "PASS_COMPLETE_REQUEST" if set(case["fields"]) == REQUIRED_FIELDS else "BLOCK_OR_CLARIFY_INCOMPLETE_REQUEST"
    if query == "access_review_deadline":
        return "5_WORKING_DAYS_FROM_REQUEST_RECEIPT"
    if query == "clarification_branch":
        return "DIRECT_SIGNED_REFUSAL" if case["direct_refusal_ground"] else "SEND_SIGNED_CLARIFICATION_AND_SUSPEND"
    if query == "clarification_timeout":
        return "SEND_SIGNED_ACCESS_REFUSAL" if case["working_days_without_response"] >= 15 else "WAIT_FOR_RESPONSE"
    if query == "dataset_availability":
        return "GRANT_ACCESS_AFTER_CONFIRMATION" if case["dataset_exists"] else "INITIATE_ARTICLE_13_1_OPERATOR_REQUIREMENT_ROUTE"
    if query == "restricted_user_case":
        if case["article13_1_part7_item2_user"] and case["pp538_case_letter"] in "абвг":
            return "BLOCK_ACCESS"
        return "CONTINUE_ELIGIBILITY_REVIEW"
    if query == "purpose_complete":
        return "TERMINATE_ACCESS" if case["purpose_achieved"] else "CONTINUE_WITHIN_PURPOSE"
    if query == "blocking":
        return "BLOCK_IMMEDIATELY_NO_NUMERIC_DEADLINE"
    if query == "retention_period":
        return "NOT_STATED_DO_NOT_INVENT"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    assert len(model["formation_rules"]) == len({row["id"] for row in model["formation_rules"]}) == 8
    assert len(model["access_rules"]) == len({row["id"] for row in model["access_rules"]}) == 15
    assert len(model["formation_threat_types"]) == 3
    assert len(model["access_blocking_grounds"]) == 3
    assert [(row["value"], row["unit"]) for row in model["deadlines"]] == [
        (30, "WORKING_DAYS"), (10, "CALENDAR_DAYS"),
        (5, "WORKING_DAYS"), (15, "WORKING_DAYS")
    ]
    assert model["verification_boundary"]["immutable_official_pdf_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0019")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"]
    assert str(FIXTURES) in source["repo_bindings"]
    assert len(fixtures["cases"]) == 24
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 8 formation rules; 15 access rules; 4 deadlines; 24 regression cases")


if __name__ == "__main__":
    main()
