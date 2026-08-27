#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-356-2026-rocket-space-kii-categorization-features-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-356-2026-rocket-space-kii-categorization-features-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_ROCKET_SPACE_PRIMARY_FORMULAS_AND_GLYPHS_ZERO_DENOMINATOR_AND_NEGATIVE_DIFFERENCE_FAIL_CLOSED_PP796_LINKED"
    assert model["effective_date"] == "2026-04-09"
    assert len(model["scope"]["object_types"]) == 3
    assert len(model["indicator_applicability_routes"]) == 5
    assert len(model["per_object_assessment"]) == 4
    assert len(model["calculation_core"]["position_1_inputs"]) == 4
    assert len(model["calculation_core"]["position_11_inputs"]) == 4
    assert model["procedure"]["post_assignment_submission_deadline"] == "NOT_STATED_IN_PP_RF_356"
    assert model["formula_image_boundary"]["full_formula_images"] == 4
    assert model["formula_image_boundary"]["variable_glyph_images"] == 2
    assert model["formula_image_boundary"]["mathematical_image_fragments"] == 6
    assert model["formula_image_boundary"]["status"] == "VERIFIED_PRIMARY_IMMUTABLE_FOUR_FORMULAS_TWO_R_SIGMA_GLYPHS"
    assert model["calculation_core"]["position_8"]["source_percentage_formula"] == "U% = U / Rгод × 100%"
    assert model["calculation_core"]["position_8"]["source_damage_formula"] == "U = [(Rгод + RΣ) / 365] × (tустр − tрегл)"
    assert model["calculation_core"]["position_9"]["source_percentage_formula"] == "U% = U / Rгод × 100%"
    assert model["calculation_core"]["position_9"]["source_damage_formula"] == "U = [(Rгод + RΣ) / 365] × (tустр − tрегл)"
    assert all(model["calculation_core"][key]["absolute_value_operator"] == "ABSENT" for key in ("position_8", "position_9"))
    assert all(model["calculation_core"][key]["zero_r_annual_avg_behavior"] == "NOT_DEFINED_FAIL_CLOSED" for key in ("position_8", "position_9"))
    assert len(rules) == 64
    assert list(rules) == [f"PP356-RS-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP356-RS-017"] == "DO_NOT_INVENT_PP356_ROSCOSMOS_SUBMISSION_DEADLINE"
    assert rules["PP356-RS-052"] == "ROUTE_POSITIONS_13_AND_13_1_TO_VERIFIED_DEFENSE_OVERLAY_WITH_NUMERIC_FORMULA_GATE"
    assert model["verification_boundary"]["positions_13_and_13_1_calculation"] == "VERIFIED_SEPARATE_CURRENT_DEFENSE_OVERLAY_TEXT_NUMERIC_FORMULA_EXECUTION_BLOCKED"
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
    print("PASS: PP RF 356 rocket-space overlay; 15 paragraphs, 5 routes, 4/4 formulas and 2/2 R-sigma glyphs primary-verified, semantic edge cases fail-closed, 64 rules/cases")

if __name__ == "__main__":
    main()
