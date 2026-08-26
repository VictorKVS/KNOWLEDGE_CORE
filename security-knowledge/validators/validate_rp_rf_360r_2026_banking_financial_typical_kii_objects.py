#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-banking-financial-rows109-128-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-banking-financial-rows109-128-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = model["rows"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_BANKING_FINANCIAL_ROWS109_128_FAIL_CLOSED"
    assert [row["row"] for row in rows] == list(range(109, 129))
    assert sum(len(row["processes"]) for row in rows) == 52
    assert len(model["row110_excluded_actors"]) == 7
    assert model["dependency_routes"]["row125"]["targets"] == [112, 113, 114]
    assert model["dependency_routes"]["row126"]["targets"] == list(range(115, 122))
    assert model["dependency_routes"]["row127"]["targets"] == [123, 124]
    assert rows[11]["literal_process_duplication_from_row119"] is True
    assert rows[10]["processes"] == rows[11]["processes"]
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-FIN-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    failures = []
    for case in fixtures["cases"]:
        actual = rules[case["rule_id"]]
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    assert model["verification_boundary"]["critical_gap_created"] == 0
    assert model["verification_boundary"]["high_gap_created"] == 0
    print("PASS: RP RF 360-r financial rows 109-128; 20 rows, 52 process groups, 7 row-110 exclusions, 3 scoped dependency routes, 64 rules/cases")

if __name__ == "__main__": main()
