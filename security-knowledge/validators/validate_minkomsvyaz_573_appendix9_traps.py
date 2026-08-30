#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-traps-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-traps-regression-v1.json")

def named(items,name): return next(x for x in items if x["name"]==name)
def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TRAPS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if m["module"]["exports"]==c["value"] else "BLOCK"
    if q=="imports": return "PASS" if m["module"]["imports"]==c["value"] else "BLOCK"
    if q=="oid": return "PASS" if m["trap_message"]["oid"]==c["value"] else "BLOCK"
    if q=="data-form": return "PASS" if m["trap_message"]["data_form"]==c["value"] else "BLOCK"
    if q=="branch-count": return "PASS" if len(m["trap_message"]["variants"])==c["value"] else "BLOCK"
    if q=="branch-tag": return "PASS" if named(m["trap_message"]["variants"],c["name"])["tag"]==c["value"] else "BLOCK"
    if q=="trap-form": return "PASS" if m["trap"]["form"]==c["value"] else "BLOCK"
    if q=="field-count": return "PASS" if len(m["trap"]["fields"])==c["value"] else "BLOCK"
    if q=="field-requiredness": return "PASS" if named(m["trap"]["fields"],c["name"])["requiredness"]==c["value"] else "BLOCK"
    if q=="field-size": return "PASS" if named(m["trap"]["fields"],c["name"])["size"][c["bound"]]==c["value"] else "BLOCK"
    if q=="rendered-field-type": return "PASS_LITERAL" if named(m["trap"]["fields"],c["name"])["rendered_type"]==c["value"] else "BLOCK"
    if q=="enum-count": return "PASS" if len(m["trap_type"]["values"])==c["value"] else "BLOCK"
    if q=="enum-value": return "PASS" if named(m["trap_type"]["values"],c["name"])["value"]==c["value"] else "BLOCK"
    if q=="trap-ack-form": return "PASS" if m["trap_ack"]["form"]==c["value"] else "BLOCK"
    if q=="correlation-comment": return "PASS" if m["trap_ack"]["published_correlation_comment"]==c["value"] else "BLOCK"
    if q=="anomaly-count": return "PASS" if len(m["rendered_anomalies"])==c["value"] else "BLOCK"
    if q=="anomaly-token": return "PASS_LITERAL" if c["value"] in [x["token"] for x in m["rendered_anomalies"]] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    cases=json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]
    rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573TRP-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573TRP-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"]
    assert not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 Traps; 64 rules, 18 evidence nodes, 2 message variants, 3 Trap fields, 6 enum values, 64 cases")

if __name__=="__main__": main()
