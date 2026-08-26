#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-communication-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-communication-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_COMMUNICATION_ROWS_84_TO_95_WITH_FUTURE_PP402_OVERLAY_BLOCKED"
    assert model["application"]["row_count"] == 12
    assert model["application"]["pp402_communication_feature_dependency"]["pre_effective_application"] == "PROHIBITED"
    assert len(objects) == 12
    assert [x["id"] for x in objects] == [f"C{i}" for i in range(84, 96)]
    assert sum(len(x["processes"]) for x in objects) == 26
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-COMM-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert objects[1]["activity_exclusion"] == ["61.20.5"]
    assert objects[2]["activity_exclusion"] == ["61.20.5"]
    assert "activity_exclusion" not in objects[3]
    assert objects[4]["activity_exclusion"] == ["61.20.5"]
    assert objects[-2]["okved"] == ["61.20.5"] and objects[-1]["okved"] == ["61.20.5"]
    assert model["verification_boundary"]["pre_effective_feature_execution"] == "BLOCKED"
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
    print("PASS: RP RF 360-r rows 84-95; 12 objects, 26 process groups, 12 activity cells, 64 rules/cases; PP402 blocked before 2026-09-01")

if __name__ == "__main__": main()
