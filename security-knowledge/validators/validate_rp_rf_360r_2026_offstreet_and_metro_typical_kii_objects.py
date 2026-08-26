#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-offstreet-and-metro-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-offstreet-and-metro-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_OFFSTREET_ROWS_71_TO_76_AND_METRO_ROWS_77_TO_83"
    assert model["application"]["row_count"] == 13
    assert model["application"]["pp796_transport_feature_dependency"]["resolved_by_this_model"] is False
    assert len(objects) == 13
    assert [x["id"] for x in objects] == [f"O{i}" for i in range(71, 77)] + [f"M{i}" for i in range(77, 84)]
    assert sum(len(x["processes"]) for x in objects) == 36
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-OM-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert all(x["okved"] == ["49.39.39"] for x in objects[:5])
    assert objects[5]["okved"] == ["49.31.25"]
    assert all(x["okved"] == ["49.31.24"] for x in objects[6:])
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
    print("PASS: RP RF 360-r rows 71-83; 13 objects, 36 process groups, 13 activity cells, 64 rules/cases; retention and PP796 boundaries retained")

if __name__ == "__main__": main()
