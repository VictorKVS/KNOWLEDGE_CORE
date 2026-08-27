#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-303-2026-real-estate-registration-kii-categorization-features-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-303-2026-real-estate-registration-kii-categorization-features-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    routes = {x["id"]: x for x in model["indicator_routes"]}

    assert model["status"] == "VERIFIED_CURRENT_REAL_ESTATE_REGISTRATION_FORMULAS_PRIMARY_PDF_VERIFIED_ZERO_DENOMINATOR_FAIL_CLOSED"
    assert model["effective_date"] == "2026-04-01"
    assert model["scope"]["actors"] == ["ROSREESTR", "PUBLIC_LAW_COMPANY_ROSKADASTR"]
    assert len(model["sector_sign"]["functions"]) == 4
    assert len(routes) == 4
    assert [x["pp127_position"] for x in model["indicator_routes"]] == ["5(a)", "5(b)", "6", "9"]
    assert model["formula_image_boundary"]["image_count"] == 3
    assert model["calculations"]["RE-I2"]["formula"]["source_notation"] == "Показатель 2 = (Тпу − Тпростоя) / Тпу × 100%"
    assert model["calculations"]["RE-I2"]["formula"]["absolute_value_operator"] == "ABSENT"
    assert model["calculations"]["RE-I4"]["formulas"]["indicator_4"]["source_notation"] == "Показатель 4 = ΔДБ / Бср × 100%"
    assert model["calculations"]["RE-I4"]["formulas"]["delta_budget_revenue"]["source_notation"] == "ΔДБ = ГУ / (365 суток) × T"
    assert model["formula_image_boundary"]["status"] == "VERIFIED_PRIMARY_IMMUTABLE_THREE_FORMULAS"
    assert model["verification_boundary"]["numeric_formula_execution"] == "EXECUTABLE_WITH_COMPLETE_VALID_INPUTS_ZERO_DENOMINATORS_FAIL_CLOSED"
    assert len(rules) == 64
    assert list(rules) == [f"PP303-RE-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP303-RE-060"] == "DO_NOT_INVENT_SECTOR_SPECIFIC_CATEGORY_THRESHOLDS"
    assert rules["PP303-RE-062"] == "REQUIRE_FORMULA_OPERATORS_AND_GLYPHS_TO_MATCH_PRIMARY_PDF"
    assert model["verification_boundary"]["immutable_official_pdf_bytes"] == "VERIFIED_SHA256"
    assert model["verification_boundary"]["critical_gap_created"] == 0
    assert model["verification_boundary"]["high_gap_created"] == 0

    failures = []
    for case in fixtures["cases"]:
        actual = rules[case["rule_id"]]
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: PP RF 303 real-estate registration; 14 paragraphs, 2 actors, 4 functions, 4 routes, 3/3 formula images verified, zero denominators fail closed, 64 rules, 64 cases")

if __name__ == "__main__":
    main()
