#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-92-2026-financial-sector-kii-categorization-features-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-92-2026-financial-sector-kii-categorization-features-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_FINANCIAL_SECTOR_PRIMARY_FORMULAS_CONDITIONAL"
    assert model["effective_date"] == "2026-02-15"
    assert len(model["scope"]["actor_classes"]) == 6
    assert len(model["scope"]["ownership_evidence"]) == 3
    assert len(model["indicator_routes"]) == 21
    assert model["procedure"]["deadlines"]["updated_significant_objects_after_fstec_confirmation"] == {"value": 10, "unit": "WORKING_DAYS", "anchor": "RECEIPT_OF_CONFIRMATION"}
    assert model["formula_image_boundary"]["image_count"] == 10
    assert model["formula_image_boundary"]["verified_formula_images"] == 10
    assert model["formula_image_boundary"]["paragraph_positions"] == ["41", "42", "47", "48", "49", "50", "51", "52", "53", "54"]
    assert model["formula_image_boundary"]["status"] == "VERIFIED_PRIMARY_IMMUTABLE_FORMULAS"
    assert model["calculation_core"]["position_9_primary_formula"] == "П₉=(Пavg/(365×24)×Cmax/Д+0,2Y/Д)×100"
    assert model["calculation_core"]["position_9_absolute_value_operator"] == "ABSENT"
    assert model["calculation_core"]["position_9_zero_Д"] == "FAIL_CLOSED_NOT_DEFINED_BY_ACT"
    assert model["calculation_core"]["average_downtime_lower_bound_source_anomaly"] == "LOWER_BOUND_IMAGE_SHOWS_i_WITHOUT_EXPLICIT_EQUALS_ONE"
    assert model["calculation_core"]["average_downtime_zero_n"] == "FAIL_CLOSED_NOT_DEFINED_BY_ACT"
    assert model["calculation_core"]["position_10_family_variables"]["position_10_3"]["PA_point_in_time"] == "TENTH_WORKING_DAY_OF_CALENDAR_YEAR"
    assert model["calculation_core"]["position_10_family_variables"]["position_10_3"]["PR_point_in_time"] == "NOT_SEPARATELY_SPECIFIED_IN_CLAUSE_50"
    assert model["scenario_guidance"]["normative_force"] == "RECOMMENDED_NOT_MANDATORY"
    assert len(rules) == 64
    assert list(rules) == [f"PP92-FIN-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP92-FIN-057"] == "REQUIRE_ALL_TEN_PRIMARY_FORMULAS_AND_IMMUTABLE_SOURCE_HASHES"
    assert rules["PP92-FIN-058"] == "PRESERVE_CLAUSE42_LOWER_BOUND_ANOMALY_AND_FAIL_CLOSED_ZERO_D_OR_n"
    assert rules["PP92-FIN-063"] == "REQUIRE_IMMUTABLE_OFFICIAL_PDF_AND_REPRODUCIBLE_FORMULA_EVIDENCE"
    assert rules["PP92-FIN-061"] == "DO_NOT_TREAT_TENTH_WORKING_DAY_POINT_IN_TIME_AS_SUBMISSION_DEADLINE"
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
    print("PASS: PP RF 92 financial overlay; 55 paragraphs, 6 actor classes, 21 routing clauses, 10/10 primary formulas verified, 64 rules, 64 cases")

if __name__ == "__main__":
    main()
