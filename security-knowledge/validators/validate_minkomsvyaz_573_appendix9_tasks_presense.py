#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-presense-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-presense-regression-v1.json")

def value(m,n): return next(x for x in m["variant"]["values"] if x["name"]==n)
def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TASKS_PRESENSE_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if m["module"]["exports"]==c["value"] else "BLOCK"
    if q=="imports": return "PASS" if m["module"]["imports"]==c["value"] else "BLOCK"
    if q=="open-fields": return "PASS" if len(m["presense_task"]["fields"])==c["value"] else "BLOCK"
    if q=="open-relation": return "PASS" if m["presense_task"]["fields"][1]["relation"]==c["value"] else "BLOCK"
    if q=="registry-count": return "PASS" if m["registry"]["variant_count"]==c["value"] else "BLOCK"
    if q=="registry-variant": return "PASS" if m["registry"]["variants"]==c["value"] else "BLOCK"
    if q=="oid": return "PASS" if m["variant"]["oid"]==c["value"] else "BLOCK"
    if q=="data-form": return "PASS" if m["variant"]["data_form"]==c["value"] else "BLOCK"
    if q=="enum-count": return "PASS" if len(m["variant"]["values"])==c["value"] else "BLOCK"
    if q=="enum-value":
        x=value(m,c["name"]); return "PASS" if x["value"]==c["value"] else "BLOCK"
    if q=="enum-purpose": return "PASS" if value(m,c["name"])["published_purpose"]==c["value"] else "BLOCK"
    if q=="anomalies": return "PASS" if m["summary"]["rendered_anomalies"]==c["value"] else "BLOCK"
    if q=="literal-spelling": return "PASS_LITERAL"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); cases=json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]; rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573TPS-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573TPS-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 TasksPresense; 64 rules, 18 evidence nodes, 1 registry variant, 5 closed enum values, 64 cases")

if __name__=="__main__": main()
