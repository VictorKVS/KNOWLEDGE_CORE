#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-21-remediation-destruction-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-21-remediation-destruction-regression-v1.json")
RKN179 = Path("security-knowledge/corpus/ru-personal-data/rkn-order-179-destruction-evidence-atomic-v1.yaml")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")

INITIAL_SOURCES = {"SUBJECT_APPEAL", "SUBJECT_REQUEST", "SUBJECT_REPRESENTATIVE_APPEAL", "SUBJECT_REPRESENTATIVE_REQUEST", "REGULATOR_REQUEST"}
INITIAL_NOTICE_FIELDS = {"INCIDENT", "PRESUMED_CAUSES", "PRESUMED_HARM", "MITIGATION_MEASURES", "AUTHORIZED_CONTACT"}


def evaluate(case):
    query = case["query"]
    if query == "initial_blocking":
        if case["source"] not in INITIAL_SOURCES:
            return "NO_PART1_APPEAL_OR_REQUEST_TRIGGER_ESTABLISHED"
        if case["finding"] == "INACCURATE_DATA" and case["rights_harm"]:
            return "DO_NOT_BLOCK_IF_RIGHTS_OR_LEGITIMATE_INTERESTS_WOULD_BE_VIOLATED"
        return "ENSURE_PROCESSOR_BLOCKS_FROM_RECEIPT_FOR_VERIFICATION" if case["processor"] else "BLOCK_FROM_RECEIPT_FOR_VERIFICATION"
    if query == "clarification":
        if not case["confirmed"]:
            return "CONTINUE_VERIFICATION_NO_CORRECTION_TRIGGER_CONFIRMED"
        if case["working_days"] > 7:
            return "BLOCK_SEVEN_WORKING_DAY_DEADLINE_BREACHED"
        return "PASS_CLARIFIED_AND_UNBLOCKED" if case["block_lifted"] else "BLOCK_MUST_LIFT_AFTER_CLARIFICATION"
    if query == "unlawful_remediation":
        if case["working_days_to_stop"] > 3:
            return "BLOCK_THREE_WORKING_DAY_DEADLINE_BREACHED"
        if case["lawfulness_can_be_ensured"]:
            return "PASS_STOP_OR_REMEDIATE_WITHIN_THREE_WORKING_DAYS"
        return "PASS_DESTROY_WITHIN_TEN_WORKING_DAYS_FROM_DETECTION" if case["working_days_to_destroy"] <= 10 else "BLOCK_TEN_WORKING_DAY_DEADLINE_BREACHED"
    if query == "remediation_notice":
        if not case["subject_notified"]:
            return "BLOCK_SUBJECT_NOTICE_REQUIRED"
        if case["regulator_forwarded"] and not case["regulator_notified"]:
            return "BLOCK_REGULATOR_NOTICE_REQUIRED"
        return "PASS_SUBJECT_AND_REGULATOR_NOTICE" if case["regulator_forwarded"] else "PASS_SUBJECT_NOTICE"
    if query == "remediation_notice_deadline":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "incident_trigger":
        return "INCIDENT_ROUTE" if case["transfer_or_provision_or_dissemination_or_access"] and case["rights_violation"] else "NO_PART3_1_TRIGGER_RIGHTS_VIOLATION_NOT_ESTABLISHED"
    if query == "incident_initial":
        if case["hours"] > 24:
            return "BLOCK_24_HOUR_DEADLINE_BREACHED"
        return "PASS" if set(case["fields"]) == INITIAL_NOTICE_FIELDS else "BLOCK_INITIAL_NOTICE_FIELDS_INCOMPLETE"
    if query == "incident_followup":
        if case["hours"] > 72:
            return "BLOCK_72_HOUR_DEADLINE_BREACHED"
        if not case["investigation_results"]:
            return "BLOCK_INVESTIGATION_RESULTS_REQUIRED"
        if case["causing_persons_available"] and not case["causing_persons_reported"]:
            return "BLOCK_AVAILABLE_CAUSING_PERSONS_MUST_BE_REPORTED"
        return "PASS"
    if query == "incident_clock_origin":
        return "CLOCK_FROM_DETECTION"
    if query == "purpose_achieved":
        if case["exception"]:
            return "ROUTE_TO_CONTRACT_AGREEMENT_OR_STATUTORY_BASIS"
        if case["days"] > 30:
            return "BLOCK_30_DAY_DEADLINE_BREACHED"
        return "PASS" if case["ceased"] and case["destroyed"] else "BLOCK_CESSATION_AND_DESTRUCTION_REQUIRED"
    if query == "consent_withdrawal":
        if case["exception"]:
            return "ROUTE_TO_CONTRACT_AGREEMENT_OR_STATUTORY_BASIS"
        if case["days"] > 30:
            return "BLOCK_30_DAY_DEADLINE_BREACHED"
        if not case["ceased"]:
            return "BLOCK_CESSATION_REQUIRED"
        if not case["retention_still_required"] and not case["destroyed"]:
            return "BLOCK_DESTRUCTION_REQUIRED"
        return "PASS_CEASED_DESTRUCTION_CONDITION_NOT_MET" if case["retention_still_required"] else "PASS"
    if query == "cessation_demand":
        if case["exception"]:
            return "ROUTE_TO_ENUMERATED_STATUTORY_EXCEPTION"
        if not case["ceased"]:
            return "BLOCK_CESSATION_REQUIRED"
        if case["working_days"] <= 10:
            return "PASS"
        if not case["reasoned_extension_notice"]:
            return "BLOCK_REASONED_EXTENSION_NOTICE_REQUIRED" if case["working_days"] <= 15 else "BLOCK_TEN_WORKING_DAY_DEADLINE_BREACHED"
        return "PASS_EXTENDED" if case["working_days"] <= 15 else "BLOCK_MAXIMUM_EXTENSION_BREACHED"
    if query == "destruction_impossible":
        if not case["blocked"]:
            return "BLOCK_INTERIM_BLOCKING_REQUIRED"
        if case["federal_override"]:
            return "ROUTE_TO_OTHER_PERIOD_ESTABLISHED_BY_FEDERAL_LAW"
        return "PASS_FALLBACK" if case["months"] <= 6 else "BLOCK_SIX_MONTH_DEADLINE_BREACHED"
    if query == "destruction_fallback_scope":
        return "REJECT_SIX_MONTH_PERIOD_IS_NOT_DEFAULT"
    if query == "destruction_confirmation":
        return "PASS_REGULATOR_REQUIREMENTS_ROUTE" if case["rkn179_package_complete"] else "BLOCK_CONFIRMATION_REQUIREMENTS_INCOMPLETE"
    if query == "processor_responsibility":
        return "BLOCK_OPERATOR_MUST_ENSURE_PROCESSOR_ACTION" if case["processor_used"] and not case["operator_only_recorded_instruction"] else "PASS"
    if query == "deadline_origin":
        return "REJECT_ORIGIN_IS_UNLAWFUL_PROCESSING_DETECTION"
    if query == "deadline_unit":
        return "30_DAYS_SOURCE_DOES_NOT_SAY_WORKING_DAYS"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rkn179 = yaml.safe_load(RKN179.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 22
    assert len(model["deadlines"]) == len({row["id"] for row in model["deadlines"]}) == 10
    assert len(model["event_deadlines_without_numeric_value"]) == 3
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 14
    assert len(model["conflict_and_definition_checks"]) == 9
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["source"]["consolidating_law"]["official_publication"]["number"] == "0001202207140080"
    assert model["source"]["consolidating_law"]["general_effective_from"] == "2022-09-01"
    assert model["source"]["consolidating_law"]["article_21_part_7_effective_from"] == "2023-03-01"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    assert rkn179["id"] == "RU-RKN179-DESTRUCTION-EVIDENCE-ATOMIC-V1"

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0001")
    assert source["state"] == "ATOMIZED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-22")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
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
    print("PASS: 22 atomic rules; 10 numeric deadlines; 3 event deadlines; 14 evidence nodes; 9 conflict checks; 52 cases")


if __name__ == "__main__":
    main()
