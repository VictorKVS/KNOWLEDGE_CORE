#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/mindigital-order-173-2026-requirement-guidance-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/mindigital-order-173-2026-requirement-guidance-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
RESEARCH_CORE = {"EVIDENCE_RESEARCH_ASSIGNMENT", "EVIDENCE_RESEARCH_MATERIALS", "EVIDENCE_THREAT_AND_ATTACK_REVIEW"}


def evaluate(case):
    query = case["query"]
    if query == "standing_operator_duty":
        return "ROUTE_TO_SIGNED_REQUIREMENT_AND_PP966" if case["individualized_requirement"] else "BLOCK_NO_STANDING_DUTY"
    if query == "requirement_minimum":
        return "PASS_STATUTORY_MINIMUM" if set(case["fields"]) == {"ANONYMIZED_DATA_LIST", "DELIVERY_DEADLINES"} else "BLOCK_MISSING_DELIVERY_DEADLINES"
    if query == "operator_deadline":
        return "READ_FROM_SIGNED_INDIVIDUALIZED_REQUIREMENT"
    if query == "internal_lead_time":
        return "30_CALENDAR_DAYS_BEFORE_DRAFT_CONCURRENCE_UNLESS_INSTRUCTION_SETS_OTHER_PERIOD"
    if query == "threshold":
        return "EXAMPLE_NOT_UNIVERSAL_THRESHOLD"
    if query == "h3_levels":
        return "OPTIONAL_RESEARCH_NOT_MANDATED_METHOD"
    if query == "four_operator_factor":
        return "CONTEXTUAL_MOBILE_DATA_FACTOR_NOT_UNIVERSAL_MINIMUM"
    if query == "formation_case":
        return "ALLOW_REQUIREMENT_PREPARATION_WORKFLOW" if case["pp538_case"] else "BLOCK_MISSING_PP538_CASE"
    if query == "threat_route":
        return "ROUTE_TO_PP961_THREAT_TYPES"
    if query == "transmission_route":
        return "ROUTE_TO_PP966"
    if query == "anonymization_route":
        return "ROUTE_TO_PP1154"
    if query == "instrument_effect":
        return "METHODOLOGICAL_RECOMMENDATIONS"
    if query in {"official_publication", "minjust_registration"}:
        return "NOT_LOCATED_DO_NOT_INVENT"
    if query in {"sanction", "retention_period"}:
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "research_evidence":
        return "PASS_RESEARCH_EVIDENCE_CORE" if set(case["evidence"]) == RESEARCH_CORE else "BLOCK_INCOMPLETE_RESEARCH_EVIDENCE_CORE"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    assert len(model["guidance_rules"]) == len({row["id"] for row in model["guidance_rules"]}) == 16
    assert len(model["research_work"]["appendix_sections"]) == 6
    assert model["authority_boundary"]["instrument_effect"] == "METHODOLOGICAL_RECOMMENDATIONS"
    assert model["verification_boundary"]["official_publication_identity"] == "NOT_LOCATED_IN_BOUNDED_SEARCH"
    assert model["verification_boundary"]["minjust_registration"] == "NOT_LOCATED_IN_BOUNDED_SEARCH"
    assert [(row["value"], row["unit"], row["operator_deadline"]) for row in model["workflow_deadlines"]] == [(30, "CALENDAR_DAYS", False)]
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0021")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"]
    assert str(FIXTURES) in source["repo_bindings"]
    assert len(fixtures["cases"]) == 22
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 16 guidance clauses; 6 appendix sections; 1 internal clock; 22 regression cases")


if __name__ == "__main__":
    main()

