#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59711-2022-impact-criteria-core-part5-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59711-2022-impact-criteria-core-part5-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["control_rules"]}
    expected_ids = []
    for clause, count in [("A.1", 15), ("A.2", 12), ("A.3", 5), ("A.4", 16), ("A.5", 6), ("A.6", 9), ("A.7", 7)]:
        expected_ids.extend(f"G59711-{clause}-{i:03d}" for i in range(1, count + 1))
    assert list(rules) == expected_ids
    assert len(rules) == 70
    assert len(fixtures["cases"]) == 64

    def evaluate(case):
        query = case["query"]
        if query == "metric":
            return model["coverage"][case["property"]]
        if query == "status":
            return model["status"]
        if query == "boundary":
            return model["verification_boundary"][case["property"]]
        if query == "gap_boundary":
            return {
                "critical": model["verification_boundary"]["critical_gap_created"],
                "high": model["verification_boundary"]["high_gap_created"],
            }
        if query == "taxonomy_length":
            return len(model[case["section"]][case["property"]])
        if query == "taxonomy_property":
            return model[case["section"]][case["property"]][case["index"]]
        if query == "model_property":
            return model[case["section"]][case["property"]]
        if query == "source_property":
            return model["source_evidence"][case["section"]][case["property"]]
        if query == "profile_property":
            return model["literal_2022_profiles"][case["profile"]][case["property"]]
        if query == "nested_property":
            value = model
            for part in case["path"]:
                value = value[part]
            return value
        if query == "rule_property":
            return rules[case["rule"]][case["property"]]
        if query == "clause_rule_count":
            prefix = f"G59711-{case['clause_prefix']}-"
            return sum(rule_id.startswith(prefix) for rule_id in rules)
        if query == "guard":
            return case["guard"] in model["scope_guards"]
        raise AssertionError(query)

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: mandatory appendix A; 7 units, 70 rules, 5 criteria, 64 cases; current KII use fail-closed")


if __name__ == "__main__":
    main()
