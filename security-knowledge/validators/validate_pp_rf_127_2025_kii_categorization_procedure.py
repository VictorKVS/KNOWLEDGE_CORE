#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/pp-rf-127-2025-kii-categorization-procedure-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/pp-rf-127-2025-kii-categorization-procedure-regression-v1.json")

def dig(obj, path):
    for part in path.split("."):
        obj = obj[part]
    return obj

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x["rule"] for x in model["control_rules"]}
    inputs = {x["id"]: x for x in model["procedure"]["input_data"]}
    fields = {x["id"]: x for x in model["submission"]["required_fields"]}
    assert list(rules) == [f"PP127-PROC-{i:03d}" for i in range(1, 97)]
    assert len(fixtures["cases"]) == 64

    def evaluate(case):
        q = case["query"]
        if q == "metric": return model["coverage"][case["property"]]
        if q == "status": return model["status"]
        if q == "applicability": return model["procedure"]["applicability"][case["property"]]
        if q == "decision": return model["procedure"]["decision_logic"][case["property"]]
        if q == "created": return model["procedure"]["created_object_route"][case["property"]]
        if q == "length": return len(dig(model, case["path"]))
        if q == "input": return inputs[case["id"]][case["property"]]
        if q == "commission": return model["commission"][case["property"]]
        if q == "commission_member": return model["commission"]["mandatory_members"][case["index"]][case["property"]]
        if q == "branch": return model["commission"]["branch_commissions"][case["property"]]
        if q == "scenario": return model["scenario_model"][case["property"]]
        if q == "act": return model["act"][case["property"]]
        if q == "deadline": return dig(model, case["path"])[case["property"]]
        if q == "field": return fields[case["id"]][case["property"]]
        if q == "monitoring": return model["authority_and_monitoring"][case["property"]]
        if q == "engaged": return model["authority_and_monitoring"]["engaged_subordinate_organizations"][case["property"]]
        if q == "periodic": return model["lifecycle"]["periodic_review"][case["property"]]
        if q == "new_unlisted": return model["lifecycle"]["new_unlisted_object"][case["property"]]
        if q == "rule": return rules[case["id"]]
        if q == "boundary": return model["verification_boundary"][case["property"]]
        if q == "gap": return {"critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        raise AssertionError(q)

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: PP RF 127 current procedure; 30 units, 96 rules, 8 repealed items blocked, 64 cases")

if __name__ == "__main__":
    main()
