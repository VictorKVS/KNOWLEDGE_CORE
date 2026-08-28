#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/search-timing-tables-and-combined-queries-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/search-timing-tables-and-combined-queries-regression-v1.json")


def evaluate(case, model):
    query = case["query"]
    if query == "table1":
        rows = {row["id"]: row for row in model["table1_rows"]}
        row = rows.get(case["row"])
        if row is None:
            return "BLOCK_UNKNOWN_ROW"
        periods = {period["id"] for period in model["table1_periods"]}
        if case["period"] not in periods:
            return "BLOCK_UNKNOWN_PERIOD"
        limit = row["limits_seconds"][case["period"]]
        if limit is None:
            return "PENDING_NOT_SPECIFIED"
        return "PASS" if case["actual_seconds"] < limit else "BLOCK_STRICT_LIMIT"
    if query == "table2":
        if date.fromisoformat(case["date"]) < date(2024, 3, 1):
            return "NOT_YET_EFFECTIVE"
        records = case["records"]
        if not isinstance(records, int) or isinstance(records, bool) or records < 0:
            return "BLOCK_INVALID_RECORD_COUNT"
        band = next(
            (
                item
                for item in model["table2_result_delivery"]["bands"]
                if item["records_min"] <= records <= item["records_max"]
            ),
            None,
        )
        if band is None:
            return "OUT_OF_TABLE_FAIL_CLOSED"
        return "PASS" if case["actual_seconds"] < band["max_seconds"] else "BLOCK_STRICT_LIMIT"
    if query == "concurrency":
        if case["tasks"] < model["concurrency"]["minimum_simultaneous_tasks"]:
            return "BLOCK_MINIMUM_CAPACITY"
        if case["tasks"] > 100 and case["timing_for_all"]:
            return "TIMING_ABOVE_100_NOT_SPECIFIED"
        return "PASS"
    if query == "combined":
        operator = case["operator"]
        if operator == "NOT" and not case["not_admissible"]:
            return "BLOCK_NOT_ADMISSIBILITY"
        if operator in {"AND", "GROUPED_AND"}:
            return "PASS" if case["actual_seconds"] < case["reference_seconds"] else "BLOCK_STRICT_LIMIT"
        if operator in {"OR", "NOT"}:
            return "PASS" if case["actual_seconds"] <= case["reference_seconds"] else "BLOCK_LIMIT"
        return "BLOCK_UNKNOWN_OPERATOR"
    raise AssertionError(query)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 48
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 18
    assert len(model["table1_rows"]) == 4
    assert len(model["table1_periods"]) == 5
    assert len(model["table2_result_delivery"]["bands"]) == 10
    assert model["table1_rows"][1]["limits_seconds"]["UP_TO_THREE_YEARS"] == 5400
    assert model["table1_rows"][2]["limits_seconds"]["UP_TO_ONE_MONTH"] is None
    assert model["table1_rows"][3]["limits_seconds"]["UP_TO_THREE_YEARS"] is None
    assert model["combined_queries"]["timing"]["AND"]["comparator"] == "LT"
    assert model["combined_queries"]["timing"]["OR"]["comparator"] == "LE"
    assert model["combined_queries"]["timing"]["NOT"]["comparator"] == "LE"
    assert model["table2_result_delivery"]["effective_from"] == "2024-03-01"
    assert model["table2_result_delivery"]["bands"][-1]["records_max"] == 1000000
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 64
    assert len({case["id"] for case in fixtures["cases"]}) == 64
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print(
        "PASS: Order 573 section IV; 48 rules, 18 evidence nodes, 64 cases; "
        "Table 1 strict sparse matrix, combined-query comparators and Order 630 Table 2 verified"
    )


if __name__ == "__main__":
    main()
