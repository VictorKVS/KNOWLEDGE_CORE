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

    assert model["status"] == "VERIFIED_CURRENT_REAL_ESTATE_REGISTRATION_TEXT_FORMULA_IMAGES_BLOCKED"
    assert model["effective_date"] == "2026-04-01"
    assert model["scope"]["actors"] == ["ROSREESTR", "PUBLIC_LAW_COMPANY_ROSKADASTR"]
    assert len(model["sector_sign"]["functions"]) == 4
    assert len(routes) == 4
    assert [x["pp127_position"] for x in model["indicator_routes"]] == ["5(a)", "5(b)", "6", "9"]
    assert model["formula_image_boundary"]["image_count"] == 3
    assert model["calculations"]["RE-I2"]["formula"] == "PENDING_FORMULA_IMAGE_BYTES"
    assert model["calculations"]["RE-I4"]["formulas"]["budget_revenue_reduction"] == "PENDING_FORMULA_IMAGE_BYTES"
    assert model["verification_boundary"]["numeric_formula_execution"] == "BLOCKED_FAIL_CLOSED"
    assert len(rules) == 64
    assert list(rules) == [f"PP303-RE-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP303-RE-060"] == "DO_NOT_INVENT_SECTOR_SPECIFIC_CATEGORY_THRESHOLDS"
    assert rules["PP303-RE-062"] == "DO_NOT_CLAIM_FORMULA_VERIFICATION_FROM_VARIABLE_DESCRIPTIONS"
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
    print("PASS: PP RF 303 real-estate registration; 14 paragraphs, 2 actors, 4 functions, 4 routes, 3 formula images blocked, 64 rules, 64 cases")

if __name__ == "__main__":
    main()
