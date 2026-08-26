#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-science-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-science-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}

    assert model["status"] == "VERIFIED_CURRENT_SCIENCE_ROWS_13_TO_21"
    assert model["edition_date"] == "2026-05-27"
    assert model["application"]["row_count"] == 9
    assert model["application"]["amendment_1237r_science_effect"] == "NONE"
    assert model["application"]["technology_readiness"]["automatic_category_effect"] == "NONE"
    assert len(objects) == 9
    assert [x["id"] for x in objects] == [f"S{i}" for i in range(13, 22)]
    assert [x["global_row"] for x in objects] == list(range(13, 22))
    assert sum(len(x["processes"]) for x in objects) == 28
    assert all(len(x["processes"]) == len(x["process_profiles"]) for x in objects)
    assert objects[0]["okved"] == ["84"]
    assert all(x["okved"] == ["72"] for x in objects[1:])
    assert len(model["condition_profiles"]["IMPACT_FOUR"]) == 4
    assert len(model["condition_profiles"]["SAFETY_THREE"]) == 3
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-S-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
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
    print("PASS: RP RF 360-r science rows 13-21; 28 processes, 9 activity cells, 3 profiles, 64 rules/cases")

if __name__ == "__main__":
    main()
