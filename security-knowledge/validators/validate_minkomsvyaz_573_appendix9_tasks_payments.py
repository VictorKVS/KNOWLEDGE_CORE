#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-payments-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-payments-regression-v1.json")

def choice(m,n): return m["parameter_choices"][n]
def field(m,n,f): return next(x for x in choice(m,n) if x["name"]==f)
def variant(m,n): return next(x for x in m["registry"]["variants"] if x["name"]==n)

def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TASKS_PAYMENTS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if m["module"]["exports"]==c["value"] else "BLOCK"
    if q=="open-fields": return "PASS" if len(m["payments_task"]["fields"])==c["value"] else "BLOCK"
    if q=="registry-count": return "PASS" if len(m["registry"]["variants"])==c["value"] else "BLOCK"
    if q=="variant":
        x=variant(m,c["name"]); return "PASS" if (x["oid"],x["data"])==(c["oid"],c["data"]) else "BLOCK"
    if q=="sequence-count": return "PASS" if len(m["parameter_sequences"])==c["value"] else "BLOCK"
    if q=="choice-count": return "PASS" if len(m["parameter_choices"])==c["value"] else "BLOCK"
    if q=="branch-count": return "PASS" if len(choice(m,c["name"]))==c["value"] else "BLOCK"
    if q=="field":
        x=field(m,c["choice"],c["name"]); return "PASS" if (x["tag"],x["type"])==(c["tag"],c["type"]) else "BLOCK"
    if q=="size": return "PASS" if field(m,c["choice"],c["name"])["size"]==c["value"] else "BLOCK"
    if q=="anomalies": return "PASS" if len(m["rendered_anomalies"])==c["value"] else "BLOCK"
    if q=="summary-branches": return "PASS" if m["summary"]["unique_choice_branches"]==c["value"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]; cases=f["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573TP-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573TP-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 TasksPayments; 64 rules, 18 evidence nodes, 10 variants, 8 parameter choices, 26 unique branches, 64 cases")

if __name__=="__main__": main()
