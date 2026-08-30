#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-unformatted-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-unformatted-regression-v1.json")
def named(items,name): return next(x for x in items if x["name"]==name)
def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_UNFORMATTED_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if m["module"]["exports"]==c["value"] else "BLOCK"
    if q=="imports-count": return "PASS" if sum(map(len,m["module"]["imports"].values()))==c["value"] else "BLOCK"
    if q=="oid": return "PASS" if m["unformatted_message"]["oid"]==c["value"] else "BLOCK"
    if q=="top-count": return "PASS" if len(m["unformatted_message"]["variants"])==c["value"] else "BLOCK"
    if q=="top-tag": return "PASS" if named(m["unformatted_message"]["variants"],c["name"])["tag"]==c["value"] else "BLOCK"
    if q=="request-field-count": return "PASS" if len(m["raw_request"]["fields"])==c["value"] else "BLOCK"
    if q=="request-field": return "PASS" if named(m["raw_request"]["fields"],c["name"])["type"]==c["type"] else "BLOCK"
    if q=="request-task-count": return "PASS" if len(m["raw_request_task"]["variants"])==c["value"] else "BLOCK"
    if q=="request-tag": return "PASS" if named(m["raw_request_task"]["variants"],c["name"])["tag"]==c["value"] else "BLOCK"
    if q=="raw-type-count": return "PASS" if len(m["raw_data_type"]["values"])==c["value"] else "BLOCK"
    if q=="raw-type-value": return "PASS" if named(m["raw_data_type"]["values"],c["name"])["value"]==c["value"] else "BLOCK"
    if q=="data-start-field-count": return "PASS" if len(m["data_start_request"]["fields"])==c["value"] else "BLOCK"
    if q=="data-start-field": return "PASS" if named(m["data_start_request"]["fields"],c["name"])["type"]==c["type"] else "BLOCK"
    if q=="data-stop-form": return "PASS" if m["data_stop_request"]["form"]==c["value"] else "BLOCK"
    if q=="response-count": return "PASS" if len(m["raw_response"]["variants"])==c["value"] else "BLOCK"
    if q=="response-tag": return "PASS" if named(m["raw_response"]["variants"],c["name"])["tag"]==c["value"] else "BLOCK"
    if q=="data-types-response-field-count": return "PASS" if len(m["response_types"]["DataTypesResponse"]["fields"])==c["value"] else "BLOCK"
    if q=="boolean-response-count": return "PASS" if sum(1 for x in m["response_types"].values() if x["form"]=="BOOLEAN")==c["value"] else "BLOCK"
    if q=="report-field-count": return "PASS" if len(m["raw_report"]["fields"])==c["value"] else "BLOCK"
    if q=="report-size": return "PASS" if named(m["raw_report"]["fields"],c["name"])["size"][c["bound"]]==c["value"] else "BLOCK"
    if q=="report-range": return "PASS" if named(m["raw_report"]["fields"],c["name"])["range"][c["bound"]]==c["value"] else "BLOCK"
    if q=="block-variant-count": return "PASS" if len(m["raw_data_block"]["variants"])==c["value"] else "BLOCK"
    if q=="block-tag": return "PASS" if named(m["raw_data_block"]["variants"],c["name"])["tag"]==c["value"] else "BLOCK"
    if q=="raw-bytes-block-form": return "PASS" if m["raw_bytes_block"]["form"]==c["value"] else "BLOCK"
    if q=="raw-bytes-size": return "PASS" if m["raw_bytes"]["size"][c["bound"]]==c["value"] else "BLOCK"
    if q=="anomaly-count": return "PASS" if len(m["rendered_anomalies"])==c["value"] else "BLOCK"
    if q=="anomaly-token": return "PASS_LITERAL" if c["value"] in [x["token"] for x in m["rendered_anomalies"]] else "BLOCK"
    if q=="unused-import": return "PASS_LITERAL" if c["value"] in m["module"]["unused_visible_imports"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); cases=json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]; rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573UNF-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573UNF-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 Unformatted; 64 rules, 18 evidence nodes, 4 routes, 4 requests, 4 responses, 4 raw types, 64 cases")
if __name__=="__main__": main()
