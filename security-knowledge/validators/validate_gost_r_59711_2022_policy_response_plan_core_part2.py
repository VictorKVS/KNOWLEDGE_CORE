#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59711-2022-policy-response-plan-core-part2-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59711-2022-policy-response-plan-core-part2-regression-v1.json")


def nested_get(model, dotted):
    value = model
    for part in dotted.split("."):
        value = value[part]
    return value


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["control_rules"]}
    expected_ids = []
    for clause, count in [("5", 8), ("6.1", 5), ("6.2", 17), ("7.1", 13), ("7.2", 45), ("7.3", 12), ("7.4", 4)]:
        expected_ids.extend(f"G59711-{clause}-{i:03d}" for i in range(1, count + 1))
    assert list(rules) == expected_ids
    assert len(rules) == 104
    assert len(fixtures["cases"]) == 64

    def evaluate(case):
        query = case["query"]
        if query == "metric": return model["coverage"][case["property"]]
        if query == "status": return model["status"]
        if query == "boundary": return model["verification_boundary"][case["property"]]
        if query == "gap_boundary":
            return {"critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        if query == "taxonomy_length": return len(nested_get(model, case["property"]))
        if query == "taxonomy_property": return nested_get(model, case["property"])
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
    print("PASS: sections 5-7.4; 7 units, 104 rules, 19 mandatory + 2 conditional plan items, 64 fail-closed cases")


if __name__ == "__main__":
    main()
