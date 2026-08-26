#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-healthcare-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-healthcare-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}

    assert model["status"] == "VERIFIED_CURRENT_HEALTHCARE_ROWS_1_TO_12_PROJECT_FEATURES_NOT_APPLIED"
    assert model["application"]["row_count"] == 12
    assert model["application"]["sectoral_categorization_features"]["project_application"] == "PROHIBITED"
    assert len(objects) == 12
    assert [x["id"] for x in objects] == [f"H{i:02d}" for i in range(1, 13)]
    assert sum(len(x["processes"]) for x in objects) == 31
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-H-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert objects[5]["okved"] == ["84.30"]
    assert objects[8]["processes"] == ["PROVIDE_ANTITUMOR_THERAPY", "CALCULATE_RADIATION_EXPOSURE_MODE"]
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
    print("PASS: RP RF 360-r healthcare rows 1-12; 31 processes, 12 activity cells, 64 rules/cases; project blocked")

if __name__ == "__main__":
    main()
