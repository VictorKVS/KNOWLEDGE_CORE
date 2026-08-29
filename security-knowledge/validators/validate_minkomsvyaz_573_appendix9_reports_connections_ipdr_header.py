#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-ipdr-header-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-ipdr-header-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)
def evaluate(c,m):
    q=c["query"]; h=m["open_type_header"]; ss=m["structures"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_IPDR_HEADER_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="outer-field-count":return "PASS" if len(h["fields"])==c["count"] and sum(not x["optional"] for x in h["fields"])==c["required"] else "BLOCK_FIELD_CONTRACT"
    if q=="outer-field":
        x=named(h["fields"],c["name"]);return "PASS_REQUIRED" if x and x["type"]==c["type"] and not x["optional"] else "BLOCK_FIELD"
    if q=="outer-object-set":
        x=named(h["fields"],c["name"]);return "PASS" if x and x["object_set"]==c["value"] else "BLOCK_OBJECT_SET"
    if q=="outer-relation":
        x=named(h["fields"],c["name"]);return "PASS" if x and x["relation"]==c["value"] else "BLOCK_RELATION"
    if q=="variant-members":return "PASS" if h["variant_set"]["closed_members"]==c["value"] else "BLOCK_VARIANTS"
    if q=="variant-member":return "PASS" if c["value"] in h["variant_set"]["closed_members"] else "BLOCK_UNKNOWN_VARIANT"
    if q=="binding-oid":return "PASS" if h["binding"]["oid"]==c["value"] else "BLOCK_OID"
    if q=="binding-data":return "PASS" if h["binding"]["data_type"]==c["value"] else "BLOCK_DATA"
    if q=="semantic":return "NOT_SPECIFIED"
    if q=="structure-count":
        f=ss[c["structure"]]["fields"];return "PASS" if len(f)==c["count"] and sum(not x["optional"] for x in f)==c["required"] else "BLOCK_FIELD_CONTRACT"
    if q=="field":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if not x:return "BLOCK_UNKNOWN_FIELD"
        if x["tag"]!=c["tag"]:return "BLOCK_TAG"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="boundary":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if "value_min" in x:return "PASS" if x["value_min"]<=c["value"]<=x["value_max"] else "BLOCK_RANGE"
        return "PASS" if x["size_min"]<=c["value"]<=x["size_max"] else "BLOCK_SIZE"
    if q=="syntax":return "PENDING_PRIMARY_PDF"
    if q=="enum":return "PASS" if ss["IP-AAAResult"]["closed_values"].get(c["label"])==c["value"] else "BLOCK_ENUM"
    if q=="reuse":return "PASS"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573HDR-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    h=m["open_type_header"]; data=m["structures"]["DataNetworkCdrHeaderData"]; aaa=m["structures"]["IP-AAAInformation"]
    assert len(h["fields"])==2 and h["variant_set"]["closed_members"]==["dataNetworkCdrHeader"]
    assert h["binding"]=={"name":"dataNetworkCdrHeader","oid":"sorm-report-connection-ipdr-header","data_type":"DataNetworkCdrHeaderData"}
    assert len(data["fields"])==7 and sum(not x["optional"] for x in data["fields"])==6
    assert named(data["fields"],"point-id")["optional"] and named(data["fields"],"point-id")["tag"] is None
    assert named(data["fields"],"protocol-code")["value_min"]==0 and named(data["fields"],"protocol-code")["value_max"]==65535
    assert len(aaa["fields"])==2 and sum(not x["optional"] for x in aaa["fields"])==1
    assert named(aaa["fields"],"username")["size_min"]==0 and named(aaa["fields"],"aaaResult")["rendered_token"]=="IP-AAAResultOPTIONAL"
    assert m["structures"]["IP-AAAResult"]["closed_values"]=={"aaaUnknown":1,"aaaFailed":2,"aaaSucceeded":3}
    cases=f["cases"];assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573HDR-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures:print(*failures,sep="\n");raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 IPDR header/open type; 64 rules, 18 evidence nodes, 7 header-data fields, 2 IP-AAA fields, 64 cases")
if __name__=="__main__":main()
