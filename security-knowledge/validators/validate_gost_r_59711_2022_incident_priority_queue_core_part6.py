#!/usr/bin/env python3
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/standards/gost-r-59711-2022-incident-priority-queue-core-part6-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-59711-2022-incident-priority-queue-core-part6-regression-v1.json")

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = {x["id"]: x for x in model["control_rules"]}
    expected = ([f"G59711-B.1-{i:03d}" for i in range(1,23)] +
                [f"G59711-B.2-{i:03d}" for i in range(1,15)] +
                [f"G59711-B.3-{i:03d}" for i in range(1,13)])
    assert list(rules) == expected and len(rules) == 48
    queues = {x["queue"]: x for x in model["response_queue_table_b1"]}
    assert list(queues) == list(range(1,10))
    assert len(fixtures["cases"]) == 64

    def evaluate(c):
        q = c["query"]
        if q == "metric": return model["coverage"][c["property"]]
        if q == "status": return model["status"]
        if q == "boundary": return model["verification_boundary"][c["property"]]
        if q == "gap": return {"critical":model["verification_boundary"]["critical_gap_created"],"high":model["verification_boundary"]["high_gap_created"]}
        if q == "priority_length": return len(model["priority_model"][c["property"]])
        if q == "priority_property": return model["priority_model"][c["property"]]
        if q == "priority_item": return model["priority_model"][c["property"]][c["index"]]
        if q == "significance_length": return len(model["infrastructure_significance"][c["property"]])
        if q == "significance_item": return model["infrastructure_significance"][c["property"]][c["index"]]
        if q == "significance_property": return model["infrastructure_significance"][c["property"]]
        if q == "scale": return model["incident_scale"][c["property"]]
        if q == "queue": return {k:v for k,v in queues[c["queue"]].items() if k != "queue"}
        if q == "absent": return model["absent_queue_combinations"][c["index"]]
        if q == "rule": return rules[c["rule"]]["rule"]
        if q == "guard": return c["guard"] in model["scope_guards"]
        raise AssertionError(q)

    failures=[]
    for c in fixtures["cases"]:
        actual=evaluate(c)
        if actual != c["expected"]: failures.append((c["id"],c["expected"],actual))
    if failures:
        for x in failures: print("FAIL",x)
        raise SystemExit(1)
    print("PASS: appendix B; 3 units, 48 rules, 9 queue routes, 64 cases, 30% overlap fail-closed")

if __name__ == "__main__": main()
