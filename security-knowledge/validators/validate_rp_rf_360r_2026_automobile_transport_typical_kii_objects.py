#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-automobile-transport-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-automobile-transport-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}

    assert model["status"] == "VERIFIED_CURRENT_AUTOMOBILE_TRANSPORT_ROWS_40_TO_48"
    assert model["application"]["row_count"] == 9
    assert model["application"]["pp796_transport_feature_dependency"]["resolved_by_this_model"] is False
    assert len(objects) == 9
    assert [x["id"] for x in objects] == [f"M{i}" for i in range(40, 49)]
    assert sum(len(x["processes"]) for x in objects) == 37
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-AUTO-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert objects[0]["okved"] == ["49.31.2", "49.39.1", "49.4"]
    assert objects[5]["okved"] == ["84.11"]
    assert objects[-1]["okved"] == ["63.11", "63.11.1"]
    assert rules["RP360R-AUTO-061"] == "EXCLUDE_STATISTICAL_INFORMATION_FROM_ROW40_CONTROL_DATA_PROCESS"
    assert model["verification_boundary"]["typical_object_list_substitution_for_feature_act"] == "PROHIBITED"
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
    print("PASS: RP RF 360-r automobile rows 40-48; 9 objects, 37 process groups, 9 activity cells, 64 rules/cases; PP796 feature dependency retained")

if __name__ == "__main__":
    main()
