#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-defense-industry-rows156-195-pp796-crosswalk-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-defense-industry-rows156-195-pp796-crosswalk-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = model["rows"]
    shared = model["shared_activity_qualification"]
    overlay = model["pp796_overlay_dependency"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_DEFENSE_ROWS156_195_PP796_TEXT_FORMULA_IMAGES_FAIL_CLOSED"
    assert [row["row"] for row in rows] == list(range(156, 196))
    assert sum(len(row["processes"]) for row in rows) == 83
    assert shared["applies_to_rows"] == list(range(157, 196))
    assert len(shared["any_route_required"]) == shared["route_count"] == 9
    assert rows[0]["activity_codes"] == ["84"]
    assert all(row.get("activity_scope") == "DEFENSE_SHARED_157_195" for row in rows[1:])
    assert overlay["effective_from"] == "2026-07-07"
    assert overlay["formula_images_blocked"] == 12
    assert overlay["variable_glyph_images_blocked"] == 1
    assert overlay["condition_expression_images_blocked"] == 1
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-DEF-{i:03d}" for i in range(1, 65)]
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
    print("PASS: RP RF 360-r defense rows 156-195 plus PP RF 796 crosswalk; 40 rows, 83 process groups, 9 activity routes, 14 image fragments blocked, 64 rules/cases")

if __name__ == "__main__": main()
