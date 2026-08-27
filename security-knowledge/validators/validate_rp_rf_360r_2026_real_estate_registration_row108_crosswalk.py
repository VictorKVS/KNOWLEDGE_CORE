#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-real-estate-registration-row108-crosswalk-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-real-estate-registration-row108-crosswalk-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    row = model["row108"]
    crosswalk = model["pp303_crosswalk"]
    assert model["status"] == "VERIFIED_CURRENT_ROW108_WITH_CURRENT_PP303_PRIMARY_FORMULAS_ZERO_DENOMINATORS_FAIL_CLOSED_CROSSWALK"
    assert row["okved"] == ["84.11.11", "84.11.12", "84.11.13"]
    assert row["automated_management_systems_in_object_column"] == "ABSENT"
    assert crosswalk["actors"] == ["ROSREESTR", "PPK_ROSKADASTR"]
    assert len(crosswalk["sector_functions"]) == 4
    assert crosswalk["pp127_routes"] == ["5(a)", "5(b)", "6", "9"]
    assert crosswalk["numeric_formula_execution"] == "EXECUTABLE_WITH_COMPLETE_VALID_INPUTS_ZERO_DENOMINATORS_FAIL_CLOSED"
    assert crosswalk["formula_images_verified"] == 3
    assert len(rules) == 48
    assert list(rules) == [f"RP360R-RE108-{i:03d}" for i in range(1, 49)]
    assert len(fixtures["cases"]) == 48
    assert model["verification_boundary"]["critical_gap_created"] == 0
    assert model["verification_boundary"]["high_gap_created"] == 0
    failures = []
    for case in fixtures["cases"]:
        actual = rules[case["rule_id"]]
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: RP RF 360-r row 108 and PP RF 303 crosswalk; 1 row, 3 activity codes, 2 actors, 4 functions/routes, 3/3 formula images verified, 48 rules/cases")

if __name__ == "__main__": main()
