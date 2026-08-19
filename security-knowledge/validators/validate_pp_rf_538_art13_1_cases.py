#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/pp-rf-538-2025-art13-1-cases-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/pp-rf-538-2025-art13-1-cases-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")


CASE_MAP = {
    "а": "PP538-CASE-A", "б": "PP538-CASE-B", "в": "PP538-CASE-V",
    "г": "PP538-CASE-G", "д": "PP538-CASE-D", "е": "PP538-CASE-E",
    "ж": "PP538-CASE-ZH",
}


def evaluate(case):
    query = case["query"]
    if query == "case_route":
        return CASE_MAP.get(case["case_letter"], "BLOCK_NOT_ENUMERATED")
    if query == "formation_gate":
        if not case["enumerated_case"]:
            return "BLOCK_NOT_ENUMERATED"
        if not case["purpose_proved"]:
            return "BLOCK_MISSING_CASE_PURPOSE"
        if not case["decision_basis_proved"]:
            return "BLOCK_MISSING_DECISION_BASIS"
        if not case["non_identifiability_proved"]:
            return "BLOCK_NON_IDENTIFIABILITY_NOT_PROVED"
        return "ALLOW_CASE_BOUND_FORMATION"
    if query == "frequency_group":
        return ("A_THROUGH_G_ONE_PER_DAY_PER_CASE" if case["case_letter"] in "абвг"
                else "D_THROUGH_ZH_ONE_PER_MONTH_PER_CASE")
    if query == "frequency_limit":
        limit_period = "DAY" if case["case_letter"] in "абвг" else "MONTH"
        return ("BLOCK_PP966_FREQUENCY" if case["period"] == limit_period and case["count"] > 1
                else "ALLOW_WITHIN_PP966_FREQUENCY")
    if query == "operator_duty":
        return "NOT_CREATED_BY_PP538"
    if query == "retention_period":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "effective_date":
        return "2025-09-01_EXPLICIT"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    cases = model["cases"]
    assert len(cases) == len({row["id"] for row in cases}) == 7
    assert [row["letter"] for row in cases] == list("абвгдеж")
    groups = model["pp966_frequency_crosswalk"]
    assert len(groups) == 2
    assert [len(row["cases"]) for row in groups] == [4, 3]
    assert groups[0]["period"] == "DAY" and groups[1]["period"] == "MONTH"
    assert model["source"]["effective_from"]["basis"] == "DECREE_CLAUSE_2_EXPLICIT"
    assert model["verification_boundary"]["immutable_official_pdf_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0033")
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
    print("PASS: 7 enumerated cases; 4+3 PP966 frequency crosswalk; 20 regression cases")


if __name__ == "__main__":
    main()
