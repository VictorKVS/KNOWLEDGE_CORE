#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-transport-general-air-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-transport-general-air-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}

    assert model["status"] == "VERIFIED_CURRENT_TRANSPORT_GENERAL_ROWS_22_TO_25_AND_AIR_ROWS_26_TO_39"
    assert model["application"]["row_count"] == 18
    assert model["application"]["pp796_transport_feature_dependency"]["resolved_by_this_model"] is False
    assert len(objects) == 18
    assert [x["id"] for x in objects] == ["T22", "T23", "T24", "T25"] + [f"A{i}" for i in range(26, 40)]
    assert sum(len(x["processes"]) for x in objects) == 68
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-TA-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert objects[0]["okved"] == ["84.13"]
    assert objects[9]["okved"] == ["51.10", "51.21", "52.23.1", "61.10.4", "61.10.9", "61.20"]
    assert objects[-1]["id"] == "A39"
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
    print("PASS: RP RF 360-r transport rows 22-39; 18 objects, 68 process groups, 18 activity cells, 64 rules/cases; PP796 feature dependency retained")

if __name__ == "__main__":
    main()
