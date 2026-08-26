#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-246-2026-science-kii-categorization-features-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-246-2026-science-kii-categorization-features-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    indicators = {x["id"]: x for x in model["indicator_applicability"]}

    assert model["status"] == "VERIFIED_CURRENT_SCIENCE_SECTOR_FEATURES_PARAGRAPHS_1_TO_21"
    assert model["effective_date"] == "2026-03-15"
    assert model["scope"]["rp360r_global_rows"] == list(range(13, 22))
    assert len(model["scope"]["actors"]) == 3
    assert len(model["procedure"]["steps"]) == 3
    assert len(indicators) == 5
    assert [x["pp127_position"] for x in model["indicator_applicability"]] == ["1", "7", "9", "11", "13(1)"]
    assert model["scenario"]["science_maturity_gate"]["minimum_level"] == 7
    assert model["calculation"]["inapplicable_route"] == "DO_NOT_CALCULATE_INAPPLICABLE_INDICATOR"
    assert len(rules) == 72
    assert list(rules) == [f"PP246-SCI-{i:03d}" for i in range(1, 73)]
    assert len(fixtures["cases"]) == 64
    assert rules["PP246-SCI-066"] == "DO_NOT_TRANSFER_SCIENCE_FEATURES_TO_HEALTHCARE"
    assert rules["PP246-SCI-069"] == "DO_NOT_INVENT_SECTOR_SPECIFIC_CATEGORY_THRESHOLDS"
    assert rules["PP246-SCI-070"] == "DO_NOT_INVENT_CATEGORIZATION_OR_SUBMISSION_DEADLINE"
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
    print("PASS: PP RF 246 science; 21 paragraphs, 5 indicator routes, 9 science-row bindings, 72 rules, 64 cases")

if __name__ == "__main__":
    main()
