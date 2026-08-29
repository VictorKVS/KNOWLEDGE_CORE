#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-sms-aaa-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-sms-aaa-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)
def evaluate(c,m):
    q=c["query"]; records=m["records"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_CONNECTION_RECORDS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="record-oid":return "PASS" if records[c["record"]]["oid"]==c["value"] else "BLOCK_OID"
    if q=="record-data":
        r=records[c["record"]];return "PASS" if r["data_kind"]==c["kind"] and r["element_type"]==c["element"] else "BLOCK_DATA"
    if q=="semantic":return "NOT_SPECIFIED"
    if q=="field-count":
        f=records[c["record"]]["fields"];return "PASS" if len(f)==c["count"] and sum(not x["optional"] for x in f)==c["required"] else "BLOCK_FIELD_CONTRACT"
    if q=="field":
        x=named(records[c["record"]]["fields"],c["name"])
        if not x:return "BLOCK_UNKNOWN_FIELD"
        if x["tag"]!=c["tag"]:return "BLOCK_TAG"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="tag-sequence":return "PASS" if records[c["record"]]["tag_sequence"]==c["value"] else "BLOCK_TAG_SEQUENCE"
    if q=="tag":
        intervals=records[c["record"]]["unassigned_tag_intervals"]
        return "BLOCK_UNASSIGNED_TAG" if any(a<=c["value"]<=b for a,b in intervals) else "PASS_ASSIGNED_TAG"
    if q=="enum":
        x=named(records[c["record"]]["fields"],c["name"]); vals=x["closed_values"]
        return "PASS" if vals.get(c["label"])==c["value"] else "BLOCK_ENUM"
    if q=="syntax":return "PENDING_PRIMARY_PDF"
    if q=="boundary":
        x=named(records[c["record"]]["fields"],c["name"])
        if "value_min" in x:return "PASS" if x["value_min"]<=c["value"]<=x["value_max"] else "BLOCK_RANGE"
        return "PASS" if x["size_min"]<=c["value"]<=x["size_max"] else "BLOCK_SIZE"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573SAA-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    sms=m["records"]["smsRecord"]; aaa=m["records"]["dataAAARecord"]
    assert sms["oid"]=="sorm-report-connection-sms" and sms["element_type"]=="SmsRecordContent" and sms["count_constraint"] is None
    assert len(sms["fields"])==18 and sum(not x["optional"] for x in sms["fields"])==8
    assert sms["tag_sequence"]==[0,1,2,3,4,5,6,7,9,10] and sms["unassigned_tag_intervals"]==[[8,8]]
    assert not named(sms["fields"],"message")["optional"] and named(sms["fields"],"message")["published_size"] is None
    assert aaa["oid"]=="sorm-report-connection-aaa-login" and aaa["element_type"]=="DataAAARecordContent" and aaa["count_constraint"] is None
    assert len(aaa["fields"])==29 and sum(not x["optional"] for x in aaa["fields"])==13
    assert aaa["tag_sequence"]==list(range(16)) and named(aaa["fields"],"aaa-login-type")["closed_values"]=={"connect":0,"disconnect":1,"lac-update":2}
    assert named(aaa["fields"],"aaa-called-number")["rendered_token"]=="aaa-called-numberUTF8String"
    assert named(aaa["fields"],"aaa-location-start")["rendered_token"]=="LocationOPTIONAL" and named(aaa["fields"],"aaa-location-end")["rendered_token"]=="LocationOPTIONAL"
    assert named(aaa["fields"],"aaa-mcc")["published_size"] is None and named(aaa["fields"],"aaa-mnc")["published_size"] is None
    cases=f["cases"];assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573SAA-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures:print(*failures,sep="\n");raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsConnections SMS/AAA; 64 rules, 18 evidence nodes, 18 SMS fields, 29 AAA fields, 64 cases")
if __name__=="__main__":main()
