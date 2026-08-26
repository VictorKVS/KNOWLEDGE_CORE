#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-maritime-and-inland-water-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-maritime-and-inland-water-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_MARITIME_AND_INLAND_WATER_ROWS_63_TO_70"
    assert model["application"]["row_count"] == 8
    assert model["application"]["pp796_transport_feature_dependency"]["resolved_by_this_model"] is False
    assert len(objects) == 8
    assert [x["id"] for x in objects] == [f"W{i}" for i in range(63, 71)]
    assert sum(len(x["processes"]) for x in objects) == 29
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-WATER-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert objects[0]["okved"] == ["52.22.16", "52.22.26"]
    assert objects[1]["okved"] == ["50.20", "50.30"]
    assert all(x["okved"] == ["52.10", "52.24"] for x in objects[2:])
    assert objects[5]["source_anomaly"] == "EXCLUSION_REFERS_TO_SHIP_LOADER_AND_IS_PRESERVED_LITERAL"
    assert model["verification_boundary"]["preserved_literal_source_anomalies"] == 1
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
    print("PASS: RP RF 360-r rows 63-70; 8 objects, 29 process groups, 8 activity cells, 64 rules/cases; row-68 literal anomaly and PP796 dependency retained")

if __name__ == "__main__": main()
