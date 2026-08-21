#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59711-2022-response-plan-exercises-core-part1-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59711-2022-response-plan-exercises-core-part1-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["control_rules"]}

    expected_ids = [f"G59711-12-{i:03d}" for i in range(1, 40)]
    assert list(rules) == expected_ids
    assert len(rules) == 39
    assert len(fixtures["cases"]) == 64

    def evaluate(case):
        query = case["query"]
        if query == "metric": return model["coverage"][case["property"]]
        if query == "status": return model["status"]
        if query == "boundary": return model["verification_boundary"][case["property"]]
        if query == "gap_boundary":
            return {"critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        if query == "taxonomy_length": return len(model["exercise_taxonomy"][case["property"]])
        if query == "matrix_property": return model["exercise_taxonomy"]["goal_form_matrix"][case["property"]]
        if query == "rule_property": return rules[case["rule"]][case["property"]]
        if query == "clause_rule_count": return sum(rule["clause"].startswith(case["clause_prefix"]) for rule in rules.values())
        if query == "guard": return case["guard"] in model["scope_guards"]
        if query == "crosswalk_count": return len(model["crosswalk"])
        if query == "crosswalk_property": return model["crosswalk"][case["index"]][case["property"]]
        raise AssertionError(query)

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: section 12; 2 units, 39 rules, 4 forms, 3 goals, 7 mappings, 64 fail-closed cases")


if __name__ == "__main__":
    main()
