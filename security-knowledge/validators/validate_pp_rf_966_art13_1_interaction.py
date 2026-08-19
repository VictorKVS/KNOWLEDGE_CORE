#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/pp-rf-966-2025-art13-1-interaction-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/pp-rf-966-2025-art13-1-interaction-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "scope":
        return "IN_SCOPE" if case["requirement_received"] else "OUT_OF_SCOPE"
    if query == "excluded_data":
        return "EXCLUDED_FROM_REQUIREMENT_ROUTE" if case["foreign_or_stateless"] and case["collected_outside_russia"] else "IN_SCOPE_REVIEW"
    if query == "review_minimum":
        return "AT_LEAST_30_WORKING_DAYS" if not case["gis_access"] and not case["smev_connected"] else "AT_LEAST_5_WORKING_DAYS"
    if query == "review_period_semantics":
        return "BLOCK_VALUES_ARE_MINIMUMS"
    if query == "requirement_frequency":
        limit = 1
        return "BLOCK" if case["count"] > limit else "ALLOW_WITHIN_LIMIT"
    if query == "operator_signature":
        return "ALLOW" if case["ukep"] else "BLOCK"
    if query == "removable_media":
        if case["direct_or_smev_available"]:
            return "BLOCK_CONDITIONAL_ROUTE"
        return "ALLOW_FALLBACK_ROUTE" if case.get("protection_measures") else "BLOCK_MISSING_PROTECTION"
    if query == "reasoned_refusal_deadline":
        return "5_WORKING_DAYS_FROM_RECEIPT"
    if query == "partial_absence":
        return "ALLOW_PARTIAL_REFUSAL" if case["available_remainder_provided"] else "BLOCK"
    if query == "repeat_requirement_deadline":
        return "15_WORKING_DAYS_FROM_DATA_RECEIPT_BY_MINISTRY"
    if query == "operator_correction_deadline":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "cabinet_crypto":
        return "ALLOW" if case["fsb_certified"] else "BLOCK"
    if query == "smev_support":
        return "ALLOW" if case["ministry_provided_software_free"] else "BLOCK_MINISTRY_DUTY"
    if query == "retention_period":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "effective_date":
        return "2025-09-01_EXPLICIT"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    rules = model["interaction_rules"]
    deadlines = model["deadlines"]
    assert len(rules) == len({row["id"] for row in rules}) == 12
    assert len(deadlines) == len({row["id"] for row in deadlines}) == 4
    assert {(row["value"], row["unit"]) for row in deadlines} == {
        (30, "WORKING_DAYS"), (5, "WORKING_DAYS"), (15, "WORKING_DAYS")
    }
    assert len(model["frequency_limits"]) == 2
    assert model["source"]["effective_from"]["basis"] == "DECREE_CLAUSE_2_EXPLICIT"
    assert model["verification_boundary"]["immutable_official_pdf_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0020")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"]
    assert str(FIXTURES) in source["repo_bindings"]
    assert len(fixtures["cases"]) == 20
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 12 interaction rules; 4 deadlines; 2 frequency limits; 20 regression cases")


if __name__ == "__main__":
    main()
