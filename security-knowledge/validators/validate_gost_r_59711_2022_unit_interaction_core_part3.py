#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59711-2022-unit-interaction-core-part3-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59711-2022-unit-interaction-core-part3-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["control_rules"]}
    expected_ids = []
    for clause, count in [("8.1", 22), ("8.2", 14), ("8.3", 16), ("8.4", 18), ("9.1", 15), ("9.2", 15)]:
        expected_ids.extend(f"G59711-{clause}-{i:03d}" for i in range(1, count + 1))
    assert list(rules) == expected_ids
    assert len(rules) == 100
    assert len(fixtures["cases"]) == 64

    def evaluate(case):
        query = case["query"]
        if query == "metric": return model["coverage"][case["property"]]
        if query == "status": return model["status"]
        if query == "boundary": return model["verification_boundary"][case["property"]]
        if query == "gap_boundary":
            return {"critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        if query == "taxonomy_length": return len(model["unit_taxonomy"][case["property"]])
        if query == "taxonomy_property": return model["unit_taxonomy"][case["property"]]
        if query == "rule_property": return rules[case["rule"]][case["property"]]
        if query == "clause_rule_count":
            prefix = f"G59711-{case['clause_prefix']}-"
            return sum(rule_id.startswith(prefix) for rule_id in rules)
        if query == "guard": return case["guard"] in model["scope_guards"]
        raise AssertionError(query)

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: sections 8-9; 6 units, 100 rules, 3 structures, 8 skill areas, 5 internal and 6 external groups, 64 cases")


if __name__ == "__main__":
    main()
