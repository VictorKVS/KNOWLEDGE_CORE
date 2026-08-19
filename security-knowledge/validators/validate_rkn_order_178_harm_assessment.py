#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/rkn-order-178-harm-assessment-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/rkn-order-178-harm-assessment-regression-v1.json")
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
    if query == "assessor":
        allowed = {"RESPONSIBLE_FOR_ORGANIZING_PROCESSING", "OPERATOR_FORMED_COMMISSION"}
        return "AUTHORIZED_ROUTE" if case["route"] in allowed else "BLOCK_NOT_RESPONSIBLE_PERSON_OR_OPERATOR_COMMISSION"
    if query == "trigger":
        if case.get("exception_applies"):
            return "TRIGGER_EXCLUDED_NEED_OTHER_FACTS"
        prefix = case["trigger"][0]
        return {"H": "HIGH", "M": "MEDIUM", "L": "LOW"}[prefix]
    if query == "combined":
        if not case["degrees"]:
            return "INSUFFICIENT_FACTS_NO_DEGREE_INVENTED"
        rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        return max(case["degrees"], key=lambda value: rank[value])
    if query == "act":
        checks = [
            ("operator_identity_address", "BLOCK_OPERATOR_IDENTITY_OR_ADDRESS_MISSING"),
            ("act_issue_date", "BLOCK_ACT_ISSUE_DATE_MISSING"),
            ("assessment_date", "BLOCK_ASSESSMENT_DATE_MISSING"),
            ("assessor_identity_position_signature", "BLOCK_ASSESSOR_IDENTITY_POSITION_OR_SIGNATURE_MISSING"),
            ("final_degree", "BLOCK_FINAL_DEGREE_MISSING"),
        ]
        for field, result in checks:
            if not case[field]:
                return result
        return "PASS"
    if query == "electronic_act":
        return "EQUIVALENT_TO_SIGNED_PAPER_ACT" if case["signed_under_63_fz"] else "NOT_EQUIVALENT_SIGNATURE_REQUIREMENT_UNPROVEN"
    if query == "numeric_formula":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "semantic_boundary":
        return "REJECT_POTENTIAL_HARM_ASSESSMENT_ONLY"
    if query == "final_degree_count":
        return "PASS_ONE_FINAL_DEGREE" if case["count"] == 1 else "BLOCK_ONE_FINAL_DEGREE_REQUIRED_USE_HIGHER"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 24
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 14
    assert len(model["conflict_and_definition_checks"]) == 6
    assert model["source"]["official_publication"]["number"] == "0001202211290004"
    assert model["source"]["minjust_registration"]["number"] == "71166"
    assert model["source"]["effective_from"] == "2023-03-01"
    assert model["source"]["valid_until_exclusive"] == "2029-03-01"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0013")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-21")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
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
    print("PASS: 24 atomic rules; 4 temporal events; 14 evidence nodes; 6 conflict checks; 40 cases")


if __name__ == "__main__":
    main()
