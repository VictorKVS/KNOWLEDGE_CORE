#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-402-2026-communication-kii-categorization-features-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-402-2026-communication-kii-categorization-features-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    assert model["status"] == "VERIFIED_ADOPTED_FUTURE_EFFECTIVE_COMMUNICATION_SECTOR_FORMULAS_PRIMARY_PDF_VERIFIED_PRE_EFFECTIVE_BLOCKED"
    assert model["effective_date"] == "2026-09-01"
    assert model["valid_until_date_as_stated"] == "2032-09-01"
    assert model["temporal_gate"]["observed_state"] == "ADOPTED_NOT_YET_EFFECTIVE"
    assert model["temporal_gate"]["pre_effective_execution"] == "BLOCKED"
    assert len(model["scope"]["object_types"]) == 3
    assert len(model["scope"]["subject_classes"]) == 4
    assert len(model["commission"]["special_representation_routes"]) == 3
    assert len(model["assessment"]["sequential_stages"]) == 3
    assert len(model["additional_input_groups"]) == 5
    assert len(model["calculation_methods"]) == 2
    assert model["formula_boundary"]["full_formula_images"] == 2
    assert model["formula_boundary"]["variable_glyph_images"] == 1
    assert model["formula_boundary"]["mathematical_image_fragments"] == 3
    assert model["formula_boundary"]["status"] == "VERIFIED_PRIMARY_IMMUTABLE_TWO_FORMULAS_AND_VARIABLE_GLYPH"
    assert model["formula_boundary"]["pre_effective_execution"] == "BLOCK_ALL_PP402_EXECUTION_BEFORE_2026_09_01"
    p8 = model["calculation_routes"]["position_8"]
    p9 = model["calculation_routes"]["position_9"]
    assert p8["source_notation_ru"] == "П₈ = |(Дфакт − Дсредний) / Дсредний| × 100"
    assert p8["normalized_expression"] == "abs((D_ACTUAL - D_AVG_5Y) / D_AVG_5Y) * 100"
    assert p8["absolute_value_operator_present"] is True
    assert p8["zero_denominator_behavior"] == "FAIL_CLOSED_NOT_DEFINED_BY_ACT"
    assert p9["source_notation_ru"] == "П₉ = ΔВыплат / Бсредний × 100"
    assert p9["normalized_expression"] == "(DELTA_PAYMENTS / B_AVG_FORECAST_3Y) * 100"
    assert p9["absolute_value_operator_present"] is False
    assert p9["zero_denominator_behavior"] == "FAIL_CLOSED_NOT_DEFINED_BY_ACT"
    assert p8["source_locator"]["official_pdf_page"] == 8
    assert p9["source_locator"]["official_pdf_page"] == 9
    assert model["source_evidence"]["immutable_official_pdf"]["sha256"] == "f666ccb125601dcf0b413ff7aed8f04dba1a74cd0f14655c98fb4f4277c345fc"
    assert len(rules) == 64
    assert list(rules) == [f"PP402-COM-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP402-COM-002"] == "BLOCK_PP402_EXECUTION_BEFORE_2026_09_01"
    assert rules["PP402-COM-041"] == "DO_NOT_INFER_ARITHMETIC_SUM_OR_UNSTATED_MULTI_SERVICE_AGGREGATION_FORMULA"
    assert rules["PP402-COM-063"] == "DO_NOT_ROUTE_PP796_POSITION_4_TO_PP402_BEFORE_2026_09_01"
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
    assert model["verification_boundary"]["formula_and_variable_glyph_images"] == "VERIFIED_PRIMARY_PDF"
    assert model["coverage"]["mathematical_image_fragments_blocked"] == 0
    print("PASS: PP RF 402 communication overlay; future-effective lifecycle, 2 formulas verified from primary PDF, pre-effective execution blocked, 64 rules, 64 cases")

if __name__ == "__main__":
    main()
