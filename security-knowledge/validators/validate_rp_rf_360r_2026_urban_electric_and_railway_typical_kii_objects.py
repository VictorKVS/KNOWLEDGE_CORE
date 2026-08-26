#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-urban-electric-and-railway-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-urban-electric-and-railway-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_URBAN_ELECTRIC_ROWS_49_TO_50_AND_RAILWAY_ROWS_51_TO_62"
    assert model["application"]["row_count"] == 14
    assert model["application"]["pp796_transport_feature_dependency"]["resolved_by_this_model"] is False
    assert len(objects) == 14
    assert [x["id"] for x in objects] == ["U49", "U50"] + [f"R{i}" for i in range(51, 63)]
    assert sum(len(x["processes"]) for x in objects) == 79
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-UR-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert objects[0]["okved"] == ["35.12", "35.13"]
    assert objects[8]["okved"] == ["49.20.1"]
    assert objects[-1]["okved"] == ["52.21.19"]
    assert model["verification_boundary"]["typical_object_list_substitution_for_feature_act"] == "PROHIBITED"
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
    print("PASS: RP RF 360-r rows 49-62; 14 objects, 79 process groups, 14 activity cells, 64 rules/cases; PP796 feature dependency retained")

if __name__ == "__main__": main()
