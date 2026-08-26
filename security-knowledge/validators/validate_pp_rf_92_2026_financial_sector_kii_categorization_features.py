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
    assert model["status"] == "VERIFIED_CURRENT_FINANCIAL_SECTOR_TEXT_FORMULA_IMAGES_BLOCKED"
    assert model["effective_date"] == "2026-02-15"
    assert len(model["scope"]["actor_classes"]) == 6
    assert len(model["scope"]["ownership_evidence"]) == 3
    assert len(model["indicator_routes"]) == 21
    assert model["procedure"]["deadlines"]["updated_significant_objects_after_fstec_confirmation"] == {"value": 10, "unit": "WORKING_DAYS", "anchor": "RECEIPT_OF_CONFIRMATION"}
    assert model["formula_image_boundary"]["image_count"] == 10
    assert model["formula_image_boundary"]["paragraph_positions"] == ["41", "42", "47", "48", "49", "50", "51", "52", "53", "54"]
    assert model["scenario_guidance"]["normative_force"] == "RECOMMENDED_NOT_MANDATORY"
    assert len(rules) == 64
    assert list(rules) == [f"PP92-FIN-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP92-FIN-057"] == "BLOCK_ALL_TEN_FORMULAS_UNTIL_EXACT_IMAGE_BYTES_ARE_VERIFIED"
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
    print("PASS: PP RF 92 financial overlay; 55 paragraphs, 6 actor classes, 21 routing clauses, 10 formula images blocked, 64 rules, 64 cases")

if __name__ == "__main__":
    main()
