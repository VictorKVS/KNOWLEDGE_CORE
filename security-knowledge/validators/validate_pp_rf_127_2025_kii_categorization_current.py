#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-127-2025-kii-categorization-current-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-127-2025-kii-categorization-current-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = {x["id"]: x for x in model["current_threshold_rows"]}
    crosswalk = {x["id"]: x for x in model["gost_appendix_a_crosswalk"]}
    rules = {x["id"]: x for x in model["control_rules"]}
    expected_rows = "S1 S2A S2B S3A S3B S3C S3D S4A S4B S5A S5B P6 P7 E8 E9 E10 E10_1 E10_2 E10_3 E10_4 E10_5 E10_6 E10_7 EC11A EC11B D12 D13A D13B D13_1 D14".split()
    assert list(rows) == expected_rows
    assert list(crosswalk) == [f"CW{i:02d}" for i in range(1, 16)]
    assert list(rules) == [f"PP127-2025-{i:03d}" for i in range(1, 71)]
    assert len(fixtures["cases"]) == 64

    def evaluate(case):
        q = case["query"]
        if q == "metric": return model["coverage"][case["property"]]
        if q == "root": return model[case["property"]]
        if q == "decision": return model["decision_core"][case["property"]]
        if q == "decision_length": return len(model["decision_core"][case["property"]])
        if q == "deadline": return model["decision_core"]["deadlines"][case["name"]][case["property"]]
        if q == "row": return rows[case["row"]][case["property"]]
        if q == "crosswalk": return crosswalk[case["entry"]][case["property"]]
        if q == "rule": return rules[case["rule"]][case["property"]]
        if q == "boundary": return model["verification_boundary"][case["property"]]
        if q == "source": return model["source_evidence"][case["section"]][case["property"]]
        raise AssertionError(q)

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: PP RF 127 current edition; 30 rows, 70 rules, 15 crosswalk entries, 64 cases")

if __name__ == "__main__":
    main()
