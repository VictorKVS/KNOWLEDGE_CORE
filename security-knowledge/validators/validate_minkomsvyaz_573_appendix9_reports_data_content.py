#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-data-content-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-data-content-regression-v1.json")
def named(items,name): return next(x for x in items if x["name"]==name)
def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTS_DATA_CONTENT_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if m["module"]["exports"]==c["value"] else "BLOCK"
    if q=="imports": return "PASS" if m["module"]["imports"]==c["value"] else "BLOCK"
    if q=="open-field-count": return "PASS" if len(m["data_content_report"]["fields"])==c["value"] else "BLOCK"
    if q=="open-relation": return "PASS" if m["data_content_report"]["fields"][1]["relation"]==c["value"] else "BLOCK"
    if q=="registry-count": return "PASS" if m["registry"]["variant_count"]==c["value"] else "BLOCK"
    if q=="registry-variant": return "PASS" if m["registry"]["variants"]==c["value"] else "BLOCK"
    if q=="oid": return "PASS" if m["variant"]["oid"]==c["value"] else "BLOCK"
    if q=="data-form": return "PASS" if m["variant"]["data_form"]==c["value"] else "BLOCK"
    if q=="element-type": return "PASS" if m["variant"]["element_type"]==c["value"] else "BLOCK"
    if q=="cardinality": return "PASS" if m["variant"]["cardinality"]==c["value"] else "BLOCK"
    if q=="record-form": return "PASS" if m["raw_record_content"]["form"]==c["value"] else "BLOCK"
    if q=="field-count": return "PASS" if len(m["raw_record_content"]["fields"])==c["value"] else "BLOCK"
    if q=="field-requiredness": return "PASS" if named(m["raw_record_content"]["fields"],c["name"])["requiredness"]==c["value"] else "BLOCK"
    if q=="field-type": return "PASS" if named(m["raw_record_content"]["fields"],c["name"])["type"]==c["value"] else "BLOCK"
    if q=="field-tag": return "PASS" if named(m["raw_record_content"]["fields"],c["name"])["tag"]==c["value"] else "BLOCK"
    if q=="rendered-field-type": return "PASS_LITERAL" if named(m["raw_record_content"]["fields"],c["name"])["rendered_type"]==c["value"] else "BLOCK"
    if q=="field-size": return "PASS" if named(m["raw_record_content"]["fields"],c["name"])["size"][c["bound"]]==c["value"] else "BLOCK"
    if q=="optional-tags": return "PASS" if [x["tag"] for x in m["raw_record_content"]["fields"] if x["requiredness"]=="OPTIONAL"]==c["value"] else "BLOCK"
    if q=="direction-count": return "PASS" if len(m["direction_enum"]["values"])==c["value"] else "BLOCK"
    if q=="direction-value": return "PASS" if named(m["direction_enum"]["values"],c["name"])["value"]==c["value"] else "BLOCK"
    if q=="anomaly-count": return "PASS" if len(m["rendered_anomalies"])==c["value"] else "BLOCK"
    if q=="anomaly-token": return "PASS_LITERAL" if c["value"] in [x["token"] for x in m["rendered_anomalies"]] else "BLOCK"
    if q=="condition-comment": return "PASS_COMMENT_ONLY" if c["contains"] in named(m["raw_record_content"]["fields"],c["name"])["published_condition_comment"] else "BLOCK"
    if q=="condition-enforcement": return "PASS" if named(m["raw_record_content"]["fields"],c["name"])["condition_enforcement"]==c["value"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); cases=json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]; rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573RDC-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573RDC-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsDataContent; 64 rules, 18 evidence nodes, 1 registry variant, 6 fields, 2 directions, 64 cases")
if __name__=="__main__": main()
