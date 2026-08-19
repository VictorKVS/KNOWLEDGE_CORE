#!/usr/bin/env python3
import json
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-17-appeal-damages-rights-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-17-appeal-damages-rights-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "trigger":
        law = case["subject_believes_152_violation"]
        rights = case["subject_believes_rights_violation"]
        if law and rights:
            return "ARTICLE17_COMBINED_TRIGGER_ROUTE"
        if law:
            return "ARTICLE17_STATUTORY_VIOLATION_APPEAL_ROUTE"
        if rights:
            return "ARTICLE17_RIGHTS_FREEDOMS_APPEAL_ROUTE"
        return "NO_ARTICLE17_TRIGGER_ASSERTED"
    if query == "prior_finding":
        return "PASS_NO_PRIOR_FINAL_FINDING_REQUIRED_TO_APPEAL" if case["subject_belief"] else "ROUTE_ON_ESTABLISHED_VIOLATION_CHECK_CLAIM_CONTEXT"
    if query == "appeal_object":
        return {
            "ACTION": "PASS_OPERATOR_ACTION_APPEAL",
            "OMISSION": "PASS_OPERATOR_OMISSION_APPEAL",
            "DECISION_DOCUMENT": "ROUTE_AS_OPERATOR_ACTION",
            "THIRD_PARTY_ONLY": "ARTICLE17_OPERATOR_OBJECT_NOT_ESTABLISHED",
        }[case["object"]]
    if query == "appeal_route":
        return {
            "AUTHORIZED_BODY": "PASS_AUTHORIZED_BODY_APPEAL",
            "COURT": "PASS_JUDICIAL_APPEAL",
            "OPERATOR_INTERNAL": "INTERNAL_ROUTE_NOT_REQUIRED_BY_ARTICLE17",
            "OTHER_REGULATOR": "BLOCK_ARTICLE17_TARGET_NOT_ESTABLISHED",
            "AUTHORIZED_BODY_THEN_COURT": "ARTICLE17_DOES_NOT_BAR_SEQUENTIAL_ROUTES",
            "COURT_THEN_AUTHORIZED_BODY": "CHECK_PROCEDURAL_LAW_ARTICLE17_NOT_MUTUALLY_EXCLUSIVE",
        }[case["target"]]
    if query == "precondition":
        if case["route"] == "COURT":
            if not case["internal_complaint_filed"] and not case["authority_complaint_filed"]:
                return "PASS_NO_MANDATORY_PRETRIAL_EXHAUSTION_IN_ARTICLE17"
            return "PASS_JUDICIAL_ROUTE"
        if case["route"] == "AUTHORIZED_BODY":
            return "PASS_AUTHORIZED_BODY_ROUTE" if case["internal_complaint_filed"] else "PASS_NO_INTERNAL_COMPLAINT_PREREQUISITE"
        return "BLOCK_ROUTE_NOT_ESTABLISHED"
    if query == "remedy":
        if case["venue"] == "AUTHORIZED_BODY":
            if case["claim"] in {"LOSSES", "MORAL_HARM"}:
                return "BLOCK_ARTICLE17_COMPENSATION_ROUTE_IS_JUDICIAL"
            return "PASS_AUTHORIZED_BODY_COMPLAINT"
        return {
            "RIGHTS_PROTECTION": "PASS_JUDICIAL_RIGHTS_PROTECTION",
            "LOSSES": "PASS_JUDICIAL_LOSSES_CLAIM",
            "MORAL_HARM": "PASS_JUDICIAL_MORAL_HARM_CLAIM",
            "LOSSES_AND_MORAL_HARM": "PASS_COMBINED_JUDICIAL_CLAIMS",
            "ADMINISTRATIVE_FINE": "ARTICLE17_DOES_NOT_CREATE_ADMINISTRATIVE_SANCTION",
        }[case["claim"]]
    if query == "award":
        return "ROUTE_TO_COURT_AWARD_RECORD" if case["court_award_already_made"] else "NO_AUTOMATIC_AWARD"
    constants = {
        "compensation_amount": "NOT_STATED_DO_NOT_INVENT",
        "proof_standard": "NOT_STATED_CHECK_APPLICABLE_PROCEDURAL_AND_CIVIL_LAW",
        "operator_liability": "ARTICLE17_RIGHTS_ROUTE_NOT_COMPLETE_LIABILITY_REGIME",
    }
    if query == "deadline":
        return "NOT_STATED_CHECK_APPLICABLE_PROCEDURAL_LAW"
    if query in constants:
        return constants[query]
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 9
    assert model["numeric_deadlines"] == []
    assert model["event_deadlines_without_numeric_value"] == []
    assert len(model["temporal_model"]) == 3
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 11
    assert len(model["conflict_and_definition_checks"]) == 12
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["verification_boundary"]["immutable_current_consolidated_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(item for item in library["sources"] if item["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-11")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert len(fixtures["cases"]) == 40
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 9 atomic rules; 0 numeric deadlines; 11 evidence nodes; 12 conflict checks; 40 cases")


if __name__ == "__main__":
    main()
