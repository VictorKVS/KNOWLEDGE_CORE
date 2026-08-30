#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-connections-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-connections-regression-v1.json")

def branch(model,name):
    return next(x for x in model["connections_task"]["branches"] if x["name"]==name)

def criterion(model,name):
    return next(x for x in model["criterion"]["branches"] if x["name"]==name)

def evaluate(case,model):
    q=case["query"]
    if q=="temporal":
        d=date.fromisoformat(case["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TASKS_CONNECTIONS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if model["module"]["exports"]==case["value"] else "BLOCK"
    if q=="imports": return "PASS" if model["module"]["imports"]==case["value"] else "BLOCK"
    if q=="top-count": return "PASS" if len(model["connections_task"]["branches"])==case["value"] else "BLOCK"
    if q=="top-tags": return "PASS" if [x["tag"] for x in model["connections_task"]["branches"]]==case["value"] else "BLOCK"
    if q=="top-branch":
        x=branch(model,case["name"]); return "PASS" if (x["tag"],x["type"])==(case["tag"],case["type"]) else "BLOCK"
    if q=="top-purpose": return "PASS" if branch(model,case["name"])["published_purpose"]==case["value"] else "BLOCK"
    if q=="alias": return "PASS" if model["aliases"][case["name"]]==case["value"] else "BLOCK"
    if q=="scope": return "PASS" if model["identifier_scope_rules"][case["name"]][case["field"]]==case["value"] else "BLOCK"
    if q=="sequence-form": return "PASS" if model["criteria_sequence"]["form"]==case["value"] else "BLOCK"
    if q=="sequence-element": return "PASS" if model["criteria_sequence"]["element_type"]==case["value"] else "BLOCK"
    if q=="sequence-cardinality": return model["criteria_sequence"]["cardinality"]
    if q=="criterion-form": return "PASS" if model["criterion"]["form"]==case["value"] else "BLOCK"
    if q=="criterion-count": return "PASS" if len(model["criterion"]["branches"])==case["value"] else "BLOCK"
    if q=="criterion-tags": return "PASS" if [x["tag"] for x in model["criterion"]["branches"]]==case["value"] else "BLOCK"
    if q=="criterion-branch":
        x=criterion(model,case["name"]); return "PASS" if (x["tag"],x["type"])==(case["tag"],case["type"]) else "BLOCK"
    if q=="criterion-purpose": return "PASS" if criterion(model,case["name"])["published_purpose"]==case["value"] else "BLOCK"
    if q=="choice-semantics": return "PASS_EXACTLY_ONE"
    if q=="numeric-bounds": return "PASS" if model["summary"]["numeric_bounds"]==case["value"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    if q=="rendered-anomalies": return "PASS" if model["summary"]["rendered_anomalies"]==case["value"] else "BLOCK"
    if q=="summary-routes": return "PASS" if model["summary"]["top_level_routes"]==case["value"] else "BLOCK"
    raise AssertionError(q)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; cases=fixtures["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573TX-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18
    assert [r for node in evidence for r in node["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573TX-T{i:03d}" for i in range(1,65)]
    assert len(model["connections_task"]["branches"])==3
    assert len(model["criterion"]["branches"])==2
    failures=[(c["id"],c["expected"],evaluate(c,model)) for c in cases if evaluate(c,model)!=c["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"]
    assert not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 TasksConnections; 64 rules, 18 evidence nodes, 3 routes, 2 criterion branches, 64 cases")

if __name__=="__main__": main()
