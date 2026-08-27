#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-atomic-energy-rows140-155-pp4-crosswalk-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-atomic-energy-rows140-155-pp4-crosswalk-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = model["rows"]
    common = model["shared_activity_code_domains"]["ATOMIC_COMMON_CODES_141_155"]
    overlay = model["pp4_overlay"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_ATOMIC_ROWS140_155_PP4_FORMULAS_PRIMARY_PDF_VERIFIED_ZERO_DENOMINATOR_FAIL_CLOSED"
    assert [row["row"] for row in rows] == list(range(140, 156))
    assert sum(len(row["processes"]) for row in rows) == 41
    assert common["applies_to_rows"] == list(range(141, 156))
    assert len(common["codes"]) == len(set(common["codes"])) == 57
    assert rows[0]["activity_codes"] == ["84"]
    assert all(row.get("activity_code_scope") == "ATOMIC_COMMON_CODES_141_155" for row in rows[1:])
    assert overlay["effective_from"] == "2026-01-24"
    assert overlay["paragraphs"] == 23
    assert len(overlay["non_applicable_indicator_positions"]) == 10
    assert len(overlay["indicator_routes"]) == 6
    assert overlay["methods"] == ["EXPERT", "ANALOGY_OR_COMPARISON", "ATTACK_MODELING", "CALCULATION"]
    assert len(overlay["method_routes"]) == 12
    assert [route["position"] for route in overlay["method_routes"]] == ["1", "2", "3", "5", "6", "7", "8", "9", "11", "12", "13", "13(1)"]
    formula_routes = [route for route in overlay["method_routes"] if "formula_status" in route]
    assert [route["formula_status"] for route in formula_routes] == ["VERIFIED_PRIMARY_PDF_IMAGE", "VERIFIED_PRIMARY_PDF_IMAGE"]
    assert formula_routes[0]["formula"]["source_notation_ru"] == "показатель = ΔД / Дср × 100"
    assert formula_routes[0]["formula"]["normalized_expression"] == "(DELTA_D / D_AVG_5Y) * 100"
    assert formula_routes[1]["formula"]["source_notation_ru"] == "значение = ΔДБ / Бср × 100"
    assert formula_routes[1]["formula"]["normalized_expression"] == "(DELTA_DB / B_AVG_FORECAST_3Y) * 100"
    assert all(route["formula"]["absolute_value_operator_present"] is False for route in formula_routes)
    assert all(route["formula"]["zero_denominator_behavior"] == "FAIL_CLOSED_NOT_DEFINED_BY_ACT" for route in formula_routes)
    assert [route["source_locator"]["official_pdf_page"] for route in formula_routes] == [9, 10]
    assert model["source_evidence"]["pp4_immutable_official_pdf"]["sha256"] == "65815147d515721d4fadaa251fb33f61c3259a1c4feed562afb50c0f1b087df4"
    assert overlay["method_routes"][6]["fallback_recovery_time_days"] == 10
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-ATOM-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    failures = []
    for case in fixtures["cases"]:
        actual = rules[case["rule_id"]]
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    assert model["verification_boundary"]["critical_gap_created"] == 0
    assert model["verification_boundary"]["high_gap_created"] == 0
    assert model["verification_boundary"]["pp4_formula_images_verified"] == 2
    assert model["verification_boundary"]["pp4_formula_images_blocked"] == 0
    print("PASS: RP RF 360-r atomic rows 140-155 plus PP RF 4; 16 rows, 41 process groups, 57 shared codes, 6 indicator routes, 4 methods, 12 method routes, 2 primary-PDF formulas verified, zero denominator fail-closed, 64 rules/cases")

if __name__ == "__main__": main()
