#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-fuel-energy-complex-rows129-139-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-fuel-energy-complex-rows129-139-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = model["rows"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_FUEL_ENERGY_COMPLEX_ROWS129_139_FAIL_CLOSED"
    assert [row["row"] for row in rows] == list(range(129, 140))
    assert sum(len(row["processes"]) for row in rows) == 31
    assert sum(len(row["activity_codes"]) for row in rows) == 32
    assert rows[-1]["excluded_systems"] == ["RETAIL_TRADE_INFORMATION_SYSTEMS", "FILLING_STATION_INFORMATION_SYSTEMS", "AUTOMOTIVE_GAS_FILLING_STATION_INFORMATION_SYSTEMS"]
    assert model["verification_boundary"]["sector_overlay_status"] == "PENDING_PRIMARY_SOURCE"
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-FEC-{i:03d}" for i in range(1, 65)]
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
    print("PASS: RP RF 360-r fuel-energy-complex rows 129-139; 11 rows, 31 process groups, 32 activity-code entries, 3 row-139 exclusions, 64 rules/cases")

if __name__ == "__main__": main()
