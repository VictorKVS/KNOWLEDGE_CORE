#!/usr/bin/env python3
import json
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-16-automated-decisions-rights-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-16-automated-decisions-rights-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "scope":
        if not case["solely_automated"]:
            return "NOT_SOLELY_AUTOMATED_CHECK_GENERAL_LAW"
        if case["legal_consequence"] and case["rights_or_interests_effect"]:
            return "ARTICLE16_COMBINED_PROTECTED_EFFECT_ROUTE"
        if case["legal_consequence"]:
            return "ARTICLE16_LEGAL_CONSEQUENCE_ROUTE"
        if case["rights_or_interests_effect"]:
            return "ARTICLE16_RIGHTS_INTERESTS_ROUTE"
        return "ARTICLE16_EFFECT_THRESHOLD_NOT_ESTABLISHED"
    if query == "technology_label":
        if case["technology"] == "AI" and not case["solely_automated"]:
            return "AI_LABEL_ALONE_DOES_NOT_TRIGGER_ARTICLE16"
        return "TECHNOLOGY_NEUTRAL_ARTICLE16_ROUTE"
    if query == "human_involvement":
        if case["documented_substantive_review"]:
            return "ROUTE_AS_NOT_SOLELY_AUTOMATED_WITH_EVIDENCE"
        return "DO_NOT_ASSUME_NOMINAL_CLICK_REMOVES_ARTICLE16"
    if query == "exception":
        if case["written_consent"]:
            return "PASS_WRITTEN_CONSENT_EXCEPTION"
        if case["federal_law"]:
            return "PASS_FEDERAL_LAW_EXCEPTION" if case["federal_law_safeguards"] else "BLOCK_FEDERAL_LAW_SAFEGUARDS_REQUIRED"
        if case["contract"]:
            return "BLOCK_CONTRACT_NOT_ARTICLE16_EXCEPTION"
        if case["internal_policy"]:
            return "BLOCK_INTERNAL_POLICY_NOT_ARTICLE16_EXCEPTION"
        return "BLOCK_SOLELY_AUTOMATED_DECISION_PROHIBITED"
    if query == "consent_form":
        return "PASS_WRITTEN_FORM" if case["consent"] and case["written"] else "BLOCK_WRITTEN_CONSENT_REQUIRED"
    if query == "federal_law_route":
        if not case["locator_present"]:
            return "BLOCK_FEDERAL_LAW_LOCATOR_REQUIRED"
        return "PASS_QUALIFYING_FEDERAL_LAW_ROUTE" if case["safeguard_measures_present"] else "BLOCK_FEDERAL_LAW_SAFEGUARDS_REQUIRED"
    if query == "processing_basis_boundary":
        return "BLOCK_SEPARATE_PROCESSING_BASIS_REQUIRED" if not case["article6_basis"] else "PASS_SEPARATE_PROCESSING_BASIS"
    if query == "part3_duties":
        checks = [
            ("procedure_explained", "BLOCK_DECISION_PROCEDURE_EXPLANATION_REQUIRED"),
            ("consequences_explained", "BLOCK_POSSIBLE_LEGAL_CONSEQUENCES_EXPLANATION_REQUIRED"),
            ("objection_opportunity", "BLOCK_OBJECTION_OPPORTUNITY_REQUIRED"),
            ("rights_protection_explained", "BLOCK_RIGHTS_PROTECTION_PROCEDURE_REQUIRED"),
        ]
        for field, result in checks:
            if not case[field]:
                return result
        return "PASS_ALL_PART3_DUTIES"
    if query == "generic_notice":
        return "BLOCK_GENERIC_NOTICE_CANNOT_REPLACE_FOUR_DUTIES" if case["generic_notice_only"] else "ROUTE_TO_FOUR_DUTY_CHECKLIST"
    if query == "objection_review":
        if not case["objection_received"]:
            return "NO_PART4_OBJECTION_TRIGGER"
        if case["days"] > 30:
            return "BLOCK_THIRTY_DAY_REVIEW_DEADLINE_BREACHED"
        if not case["reviewed"]:
            return "BLOCK_OBJECTION_REVIEW_REQUIRED"
        return "PASS_REVIEW_AND_RESULT_NOTICE" if case["result_notified"] else "BLOCK_RESULT_NOTICE_REQUIRED"
    if query == "objection_outcome":
        return "ROUTE_TO_CORRECTIVE_OUTCOME_AND_NOTICE" if case["objection_upheld"] else "NO_AUTOMATIC_REVERSAL_RESULT_NOTICE_STILL_REQUIRED"
    constants = {
        "deadline_unit": "DAYS_NOT_WORKING_DAYS",
        "result_notice_period": "NO_SEPARATE_NUMERIC_PERIOD_DO_NOT_INVENT",
        "ai_scope_boundary": "NOT_A_UNIVERSAL_AI_GOVERNANCE_RULE",
        "decision_reversal": "OBJECTION_DOES_NOT_AUTOMATICALLY_REVERSE_DECISION",
        "effect_boundary": "LEGAL_OR_RIGHTS_INTERESTS_EFFECT_REQUIRED",
        "exception_count": "WRITTEN_CONSENT_OR_QUALIFYING_FEDERAL_LAW",
    }
    if query in constants:
        return constants[query]
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 12
    assert len(model["deadlines"]) == 1
    assert model["deadlines"][0]["value"] == 30 and model["deadlines"][0]["unit"] == "DAYS"
    assert len(model["event_deadlines_without_separate_numeric_value"]) == 1
    assert len(model["temporal_model"]) == 3
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 14
    assert len(model["conflict_and_definition_checks"]) == 12
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["verification_boundary"]["immutable_current_consolidated_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(item for item in library["sources"] if item["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    automated = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-12")
    assert automated["maturity"] == "REGRESSION_PROTECTED"
    subject_rights = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-11")
    assert subject_rights["maturity"] == "EXECUTABLE"
    assert len(fixtures["cases"]) == 48
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 12 atomic rules; 1 numeric deadline; 1 event deadline; 14 evidence nodes; 12 conflict checks; 48 cases")


if __name__ == "__main__":
    main()
