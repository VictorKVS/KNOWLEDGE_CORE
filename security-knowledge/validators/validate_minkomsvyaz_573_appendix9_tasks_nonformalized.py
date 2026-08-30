#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-nonformalized-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-nonformalized-regression-v1.json")

def branch(items,name): return next(x for x in items if x["name"]==name)

def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TASKS_NONFORMALIZED_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if m["module"]["exports"]==c["value"] else "BLOCK"
    if q=="imports-count": return "PASS" if sum(len(x) for x in m["module"]["imports"].values())==c["value"] else "BLOCK"
    if q=="request-count": return "PASS" if len(m["request_choice"]["branches"])==c["value"] else "BLOCK"
    if q=="response-count": return "PASS" if len(m["response_choice"]["branches"])==c["value"] else "BLOCK"
    if q=="request-branch":
        x=branch(m["request_choice"]["branches"],c["name"]); return "PASS" if (x["tag"],x["type"])==(c["tag"],c["type"]) else "BLOCK"
    if q=="response-branch":
        x=branch(m["response_choice"]["branches"],c["name"]); return "PASS" if (x["tag"],x["type"])==(c["tag"],c["type"]) else "BLOCK"
    if q=="request-form": return "PASS" if m["requests"][c["name"]]["form"]==c["value"] else "BLOCK"
    if q=="validate-fields": return "PASS" if len(m["requests"]["ValidateNonFormalizedTask"]["fields"])==c["value"] else "BLOCK"
    if q=="report-limit": return "PASS" if m["requests"]["ValidateNonFormalizedTask"]["fields"][3]["range"]==c["value"] else "BLOCK"
    if q=="parameter-count": return "PASS" if len(m["parameters"]["NonFormalizedParameter"]["branches"])==c["value"] else "BLOCK"
    if q=="attribute-data-count": return "PASS" if len(m["attribute_data"]["branches"])==c["value"] else "BLOCK"
    if q=="attribute-data-branch":
        x=branch(m["attribute_data"]["branches"],c["name"]); return "PASS" if (x["tag"],x["type"])==(c["tag"],c["type"]) else "BLOCK"
    if q=="math-values": return "PASS" if m["math_operation"]["values"]==c["value"] else "BLOCK"
    if q=="attribute-type-values": return "PASS" if m["attribute_type"]["values"]==c["value"] else "BLOCK"
    if q=="entity-id-range": return "PASS" if m["entity_id"]["range"]==c["value"] else "BLOCK"
    if q=="entity-name-size": return "PASS" if m["responses"]["NonFormalizedEntity"]["fields"][1]["size"]==c["value"] else "BLOCK"
    if q=="attribute-name-size": return "PASS" if m["parameters"]["NonFormalizedEntityAttribute"]["fields"][0]["size"]==c["value"] else "BLOCK"
    if q=="response-alias": return "PASS" if m["responses"][c["name"]]["type"]==c["value"] else "BLOCK"
    if q=="rendered-anomalies": return "PASS" if len(m["rendered_anomalies"])==c["value"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]; cases=f["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573TNF-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573TNF-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 TasksNonFormalized; 64 rules, 18 evidence nodes, 4 request + 4 response branches, 7 attribute-data branches, 64 cases")

if __name__=="__main__": main()
