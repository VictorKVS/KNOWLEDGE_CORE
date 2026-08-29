#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-im-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-im-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)
def evaluate(c,m):
    q=c["query"]; ss=m["structures"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_IM_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="record-oid":return "PASS" if m["record"]["oid"]==c["value"] else "BLOCK_OID"
    if q=="record-data":return "PASS" if m["record"]["data_kind"]==c["kind"] and m["record"]["element_type"]==c["element"] else "BLOCK_DATA"
    if q=="semantic":return "NOT_SPECIFIED"
    if q=="structure-count":
        f=ss[c["structure"]]["fields"];return "PASS" if len(f)==c["count"] and sum(not x["optional"] for x in f)==c["required"] else "BLOCK_FIELD_CONTRACT"
    if q=="field":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if not x:return "BLOCK_UNKNOWN_FIELD"
        if x["tag"]!=c["tag"]:return "BLOCK_TAG"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="tag-sequence":return "PASS" if ss[c["structure"]]["tag_sequence"]==c["value"] else "BLOCK_TAG_SEQUENCE"
    if q=="tag":return "BLOCK_UNASSIGNED_TAG" if any(a<=c["value"]<=b for a,b in ss[c["structure"]]["unassigned_tag_intervals"]) else "PASS_ASSIGNED_TAG"
    if q=="boundary":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if "value_min" in x:return "PASS" if x["value_min"]<=c["value"]<=x["value_max"] else "BLOCK_RANGE"
        return "PASS" if x["size_min"]<=c["value"]<=x["size_max"] else "BLOCK_SIZE"
    if q=="protocol-reference":
        x=named(ss["DataImRecordContent"]["fields"],"im-protocol");return "PASS" if x["enum_reference"]==c["value"] else "BLOCK_REFERENCE"
    if q=="receiver-container":
        x=ss["ImReceivers"];return "PASS" if x["kind"]==c["kind"] and x["element_type"]==c["element"] else "BLOCK_CONTAINER"
    if q=="enum":return "PASS" if m["enums"]["ImEvent"].get(c["label"])==c["value"] else "BLOCK_ENUM"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573IM-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert m["record"]=={"name":"dataImRecord","oid":"sorm-report-connection-im","data_kind":"SEQUENCE OF","element_type":"DataImRecordContent","count_constraint":None}
    content=m["structures"]["DataImRecordContent"]; assert len(content["fields"])==15 and sum(not x["optional"] for x in content["fields"])==8
    assert content["tag_sequence"]==[0,1,5,10,11,12,13] and content["unassigned_tag_intervals"]==[[2,4],[6,9]]
    assert named(content["fields"],"im-message")["published_size"] is None and named(content["fields"],"im-nat-info")["count_constraint"] is None
    assert m["structures"]["ImReceivers"]=={"kind":"SEQUENCE OF","element_type":"ImReceiver","count_constraint":None}
    receiver=m["structures"]["ImReceiver"]["fields"]; assert len(receiver)==2 and all(not x["optional"] and x["size_min"]==1 and x["size_max"]==256 for x in receiver)
    assert m["enums"]["ImEvent"]=={"im-undefined":0,"im-send":1,"im-receive":2}
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573IM-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 IM records; 64 rules, 18 evidence nodes, 15 content fields, 2 receiver fields, 64 cases")
if __name__=="__main__":main()
