#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-energy-typical-kii-objects-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-energy-typical-kii-objects-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    objects = model["objects"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_ENERGY_ROWS_96_TO_107_WITH_ROW99_EXCLUDED"
    assert model["application"]["section_last_global_row"] == 107
    assert model["application"]["rows_108_to_112_energy_scope"] == "PROHIBITED_WRONG_SECTION"
    assert [x["row"] for x in objects] == [96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107]
    assert len(objects) == 11
    assert sum(len(x["processes"]) for x in objects) == 32
    assert model["excluded_positions"] == [{"row": 99, "former_object_context": "BOILER_HOUSE_TECHNOLOGICAL_PROCESS_CONTROL", "current_status": "EXCLUDED_BY_RP_RF_1237R", "executable": False, "former_text_reconstruction": "PROHIBITED"}]
    assert objects[2]["lifecycle"] == "CURRENT_TEXT_REPLACED_BY_RP_RF_1237R"
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-ENERGY-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    assert model["verification_boundary"]["row99_current_execution"] == "BLOCKED_EXCLUDED"
    assert model["verification_boundary"]["rows_108_to_112_energy_route"] == "BLOCKED_WRONG_SECTION"
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
    print("PASS: RP RF 360-r energy rows 96-107; 11 active objects, row 99 excluded, 32 process groups, 64 rules/cases; rows 108-112 rejected as non-energy")

if __name__ == "__main__": main()
