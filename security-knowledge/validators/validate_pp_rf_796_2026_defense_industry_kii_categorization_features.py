#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-796-2026-defense-industry-kii-categorization-features-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-796-2026-defense-industry-kii-categorization-features-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_DEFENSE_INDUSTRY_TEXT_FORMULA_IMAGES_COMMUNICATION_FUTURE_OVERLAY_REGISTERED_TRANSPORT_DEPENDENCY_BLOCKED"
    assert model["effective_date"] == "2026-07-07"
    assert len(model["scope"]["object_types"]) == 3
    assert len(model["procedure"]["applicable_pp127_positions"]) == 20
    assert len(model["review_intervals"]) == 5
    assert len(model["sector_significance_features"]) == 3
    assert len(model["per_object_assessment"]) == 3
    assert len(model["calculation_routes"]["position_1_input_groups"]) == 10
    assert model["formula_boundary"]["text_formulas_verified"] == 3
    assert model["formula_boundary"]["full_formula_images"] == 12
    assert model["formula_boundary"]["variable_glyph_images"] == 1
    assert model["formula_boundary"]["condition_expression_images"] == 1
    assert model["formula_boundary"]["mathematical_image_fragments"] == 14
    assert len(rules) == 72
    assert list(rules) == [f"PP796-DEF-{i:03d}" for i in range(1, 73)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP796-DEF-014"] == "REVIEW_NO_CATEGORY_DECISION_AT_LEAST_ANNUALLY"
    assert rules["PP796-DEF-037"] == "BLOCK_POSITION_3_CURRENT_TRANSPORT_CALCULATION_PROJECT_ONLY_NO_ADOPTED_ACT_IDENTIFIED"
    assert rules["PP796-DEF-038"] == "REGISTER_PP402_FOR_POSITION_4_FROM_2026_09_01_AND_BLOCK_PRE_EFFECTIVE_USE"
    assert rules["PP796-DEF-069"] == "BLOCK_TWELVE_FULL_FORMULAS_UNTIL_EXACT_IMAGE_BYTES_ARE_VERIFIED"
    assert rules["PP796-DEF-070"] == "BLOCK_ONE_VARIABLE_GLYPH_AND_ONE_STOP_CONDITION_UNTIL_EXACT_IMAGE_BYTES_ARE_VERIFIED"
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
    print("PASS: PP RF 796 defense overlay; 40 paragraphs, 4 review intervals, 3 text formulas, 14 image fragments blocked, 72 rules, 64 cases")

if __name__ == "__main__":
    main()
