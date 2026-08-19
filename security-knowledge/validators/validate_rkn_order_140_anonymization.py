#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/rkn-order-140-2025-anonymization-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/rkn-order-140-2025-anonymization-regression-v1.json")


def evaluate(case, model):
    q = case["query"]
    if q == "scope":
        return "EXCLUDED_ROUTE_TO_SEPARATE_REGIME" if case["article_6_part_1_clause"] == "9.1" else "IN_SCOPE_REVIEW"
    if q == "method_selection":
        catalog = {row["id"] for row in model["method_catalog"]["methods"]}
        return "ALLOWED_SEPARATELY_OR_COMBINED" if set(case["methods"]) <= catalog else "BLOCK_UNKNOWN_METHOD"
    if q == "identifier_key_storage":
        return "BLOCK" if case["same_storage"] else "ALLOW_SEPARATE"
    if q == "identifier_key_transfer":
        return "BLOCK" if case["recipient"] == "third_party" else "REQUIRES_ROLE_REVIEW"
    if q == "source_result_storage":
        return "BLOCK" if case["joint_storage"] else "ALLOW_SEPARATE"
    if q == "method_local_act":
        required = {"COMPOSITION_OR_SEMANTICS_CHANGE", "SHUFFLING", "DECOMPOSITION"}
        return "BLOCK" if case["method"] in required and not case["local_act"] else "ALLOW"
    if q == "aggregation_local_act":
        return "DO_NOT_INVENT_EXPLICIT_LOCAL_ACT_REQUIREMENT"
    if q == "aggregation_modality":
        return "OPTIONAL_ADDITIONAL"
    if q == "automated_system":
        return "ALLOW" if case["security_and_confidentiality"] else "BLOCK"
    if q == "action_accounting_form":
        return "ALLOW" if case["operator_defined"] and case["confirmable"] else "BLOCK"
    if q == "retention_period":
        return "NOT_STATED_DO_NOT_INVENT"
    if q == "reassessment_frequency":
        return "NOT_STATED_DO_NOT_INVENT"
    if q == "effective_date":
        return "2025-09-01_EXPLICIT"
    if q == "order_996_status":
        return "REPEALED_FROM_2025-09-01"
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    requirements = model["operator_requirements"]
    methods = model["method_catalog"]["methods"]
    assert len(requirements) == 14
    assert len({row["id"] for row in requirements}) == 14
    assert len(methods) == 5
    assert {row["id"] for row in methods} == {
        "IDENTIFIER_INTRODUCTION",
        "COMPOSITION_OR_SEMANTICS_CHANGE",
        "SHUFFLING",
        "DECOMPOSITION",
        "TRANSFORMATION_AGGREGATION",
    }
    assert model["source"]["effective_from"]["basis"] == "ORDER_CLAUSE_3_EXPLICIT"
    assert model["verification_boundary"]["immutable_official_pdf_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print(f"PASS: {len(requirements)} operator requirements; {len(methods)} method families; {len(fixtures['cases'])} regression cases")


if __name__ == "__main__":
    main()

