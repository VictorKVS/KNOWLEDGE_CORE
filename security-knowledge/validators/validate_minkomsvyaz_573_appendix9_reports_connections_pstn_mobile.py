#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-pstn-mobile-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-pstn-mobile-regression-v1.json")
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
    if q=="syntax":return "PENDING_PRIMARY_PDF"
    if q=="boundary":
        x=named(records[c["record"]]["fields"],c["name"])
        if "value_min" in x:return "PASS" if x["value_min"]<=c["value"]<=x["value_max"] else "BLOCK_RANGE"
        return "PASS" if x["size_min"]<=c["value"]<=x["size_max"] else "BLOCK_SIZE"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573PCM-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    p=m["records"]["pstnRecord"]; mo=m["records"]["mobileRecord"]
    assert p["oid"]=="sorm-report-connection-pstn" and p["element_type"]=="PstnRecordContent" and p["count_constraint"] is None
    assert len(p["fields"])==21 and sum(not x["optional"] for x in p["fields"])==12
    assert p["tag_sequence"]==[0,1,2,3,4,5,10,11,12,13] and p["unassigned_tag_intervals"]==[[6,9]]
    assert named(p["fields"],"dialed-digits")["tag"]==2 and not named(p["fields"],"dialed-digits")["optional"]
    assert named(p["fields"],"message")["published_size"] is None and named(p["fields"],"message")["rendered_token"]=="UTF8StringOPTIONAL"
    assert named(p["fields"],"in-abonent-type")["rendered_type"]=="Phone AbonentType"
    assert mo["oid"]=="sorm-report-connection-mobile" and mo["element_type"]=="MobileRecordContent" and mo["count_constraint"] is None
    assert len(mo["fields"])==22 and sum(not x["optional"] for x in mo["fields"])==9
    assert mo["tag_sequence"]==[0,1,2,3,4,5,6,7,8,9,10,41,42] and mo["unassigned_tag_intervals"]==[[11,40]]
    assert named(mo["fields"],"in-begin-location")["rendered_token"]=="LocationOPTIONAL"
    assert [(named(p["fields"],n)["value_min"],named(p["fields"],n)["value_max"]) for n in ["duration","call-type-id","supplement-service-id","term-cause"]]==[(0,86399),(0,4294967295),(0,4294967295),(0,16384)]
    cases=f["cases"];assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573PCM-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures:print(*failures,sep="\n");raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsConnections PSTN/mobile; 64 rules, 18 evidence nodes, 21 PSTN fields, 22 mobile fields, 64 cases")
if __name__=="__main__":main()
