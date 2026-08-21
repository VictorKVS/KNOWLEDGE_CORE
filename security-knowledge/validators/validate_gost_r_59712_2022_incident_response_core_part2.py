#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59712-2022-incident-response-core-part2-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59712-2022-incident-response-core-part2-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["control_rules"]}

    expected_ids = []
    for clause, count in [("6.2", 15), ("6.3", 16), ("6.4", 13), ("6.5", 24), ("6.6", 8)]:
        expected_ids.extend(f"G59712-{clause}-{i:03d}" for i in range(1, count + 1))
    assert list(rules) == expected_ids
    assert len(rules) == 76
    assert len(fixtures["cases"]) == 64

    def evaluate(case):
        query = case["query"]
        if query == "metric": return model["coverage"][case["property"]]
        if query == "status": return model["status"]
        if query == "boundary": return model["verification_boundary"][case["property"]]
        if query == "gap_boundary":
            return {"critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        if query == "stage_property": return model["response_stage_model"][case["stage"]][case["property"]]
        if query == "stage_list_length": return len(model["response_stage_model"][case["stage"]][case["property"]])
        if query == "rule_property": return rules[case["rule"]][case["property"]]
        if query == "clause_rule_count": return sum(rule["clause"].startswith(case["clause_prefix"]) for rule in rules.values())
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
    print("PASS: sections 6.2-6.6; 5 units, 76 rules, 64 fail-closed cases; diagrams remain PENDING")


if __name__ == "__main__":
    main()
