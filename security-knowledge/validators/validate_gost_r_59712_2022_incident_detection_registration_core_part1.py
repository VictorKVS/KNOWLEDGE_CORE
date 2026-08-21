#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59712-2022-incident-detection-registration-core-part1-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59712-2022-incident-detection-registration-core-part1-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["control_rules"]}

    def evaluate(case):
        query = case["query"]
        if query == "metric": return model["coverage"][case["property"]]
        if query == "scope_list_length": return len(model["scope"][case["property"]])
        if query == "status": return model["status"]
        if query == "boundary": return model["verification_boundary"][case["property"]]
        if query == "gap_boundary":
            return {"critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        if query == "analysis_method_ids": return list(model["analysis_methods"])
        if query == "method_property": return model["analysis_methods"][case["method"]][case["property"]]
        if query == "stage_property": return model["stage_model"][case["stage"]][case["property"]]
        if query == "rule_property": return rules[case["rule"]][case["property"]]
        if query == "rule_list_length": return len(rules[case["rule"]][case["property"]])
        if query == "rule_list_contains": return case["value"] in rules[case["rule"]][case["property"]]
        if query == "card_route_property": return model["card_routes"][case["route"]][case["property"]]
        if query == "card_format_owner": return model["card_routes"]["gossopka_card_format_and_content_owner"]
        if query == "guard": return case["guard"] in model["scope_guards"]
        raise AssertionError(query)

    assert list(rules) == [f"G59712-4-{i:03d}" for i in range(1, 8)] + [f"G59712-5-{i:03d}" for i in range(1, 44)]
    assert len(fixtures["cases"]) == 64
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: sections 4-5.3 plus 6.1 framework; 3 stages, 12 steps, 50 rules, 2 event deadlines, 64 fail-closed cases")


if __name__ == "__main__":
    main()
