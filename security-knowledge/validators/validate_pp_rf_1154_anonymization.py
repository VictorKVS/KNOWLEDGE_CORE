#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/pp-rf-1154-2025-anonymization-art13-1-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/pp-rf-1154-2025-anonymization-regression-v1.json")


def evaluate(case):
    query = case["query"]
    if query == "scope":
        return "IN_SCOPE" if case["mindigital_requirement_received"] or case["authorized_moscow_body"] else "OUT_OF_SCOPE"
    if query == "cross_regime_import":
        return "BLOCK_CROSS_REGIME_IMPORT"
    if query == "source_result_storage":
        return "BLOCK" if case["joint_storage"] else "ALLOW_SEPARATE"
    if query == "restricted_information":
        return "BLOCK" if case["included"] else "ALLOW"
    if query == "delivery_integrity":
        return "BLOCK" if case["loss_or_change"] else "ALLOW"
    if query == "restore_identity":
        return "BLOCK" if case["restores_identifiable_source"] else "ALLOW"
    if query == "software_conformity":
        return "ALLOW_METHODS_A_THROUGH_D" if case["confirmed"] else "BLOCK"
    if query == "method_e_route":
        if case["route"] == "OWN_SOFTWARE_OR_HARDWARE":
            return "AUTOMATED_AVAILABILITY_AND_PARAMETER_NOTICE"
        return "PROVIDE_TO_MINDIGITAL_INFORMATION_SYSTEM"
    if query == "operator_deadline":
        return "BLOCK_NOT_OPERATOR_DEADLINE" if case["claimed_days"] in {15, 30} else "REQUIRE_INDIVIDUAL_REQUIREMENT"
    if query == "operator_deadline_source":
        return "INDIVIDUALIZED_MINDIGITAL_REQUIREMENT"
    if query == "bank_of_russia_coordination":
        return "REQUIRED_FOR_LISTED_FINANCIAL_ENTITY" if case["listed_financial_entity"] else "NOT_AUTOMATICALLY_REQUIRED"
    if query == "dependency":
        return "ROUTE_TO_PP_961" if case["topic"] == "threat_types" else "ROUTE_TO_PP_966"
    if query == "retention_period":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "effective_date":
        return "2025-09-01_EXPLICIT"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    requirements = model["requirements"]
    methods = model["method_catalog"]["methods"]
    rules = model["workflow_rules"]
    deadlines = model["deadlines"]
    assert len(requirements) == len({row["id"] for row in requirements}) == 6
    assert len(methods) == len({row["id"] for row in methods}) == 5
    assert len(rules) == len({row["id"] for row in rules}) == 9
    numeric_clocks = [row for row in deadlines if "value" in row]
    assert {(row["value"], row["unit"]) for row in numeric_clocks} == {(30, "CALENDAR_DAYS"), (15, "CALENDAR_DAYS")}
    assert all(row["not_operator_delivery_deadline"] for row in numeric_clocks)
    operator_clock = next(row for row in deadlines if row["id"] == "OPERATOR_DELIVERY_CLOCK")
    assert operator_clock["value_source"] == "INDIVIDUALIZED_MINDIGITAL_REQUIREMENT"
    assert {row["id"] for row in model["dependencies"]} == {
        "RU_GOV_PP_961_2025", "RU_GOV_PP_966_2025", "RU_MINDIGITAL_ORDER_173_2026"
    }
    assert model["verification_boundary"]["immutable_official_pdf_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 19
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 6 requirements; 5 methods; 9 workflow rules; 2 numeric clocks; 19 regression cases")


if __name__ == "__main__":
    main()
