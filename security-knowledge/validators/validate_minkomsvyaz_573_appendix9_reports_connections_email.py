#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-email-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-email-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)
def evaluate(c,m):
    q=c["query"]; ss=m["structures"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_EMAIL_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="record-oid":return "PASS" if m["record"]["oid"]==c["value"] else "BLOCK_OID"
    if q=="record-data":return "PASS" if m["record"]["data_kind"]==c["kind"] and m["record"]["element_type"]==c["element"] else "BLOCK_DATA"
    if q=="semantic":return "NOT_SPECIFIED"
    if q=="choice":
        x=next((x for x in m["choice"]["closed_branches"] if x["name"]==c["name"]),None)
        return "PASS" if x and x["tag"]==c["tag"] and x["type"]==c["type"] else "BLOCK_UNKNOWN_BRANCH"
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
    if q=="enum-field":
        x=named(ss[c["structure"]]["fields"],c["name"]);return "PASS" if x["closed_values"].get(c["label"])==c["value"] else "BLOCK_ENUM"
    if q=="enum":return "PASS" if m["enums"]["EmailEvent"].get(c["label"])==c["value"] else "BLOCK_ENUM"
    if q=="container":
        x=ss[c["structure"]]["fields"][0];return "PASS" if x["item_size_min"]<=c["item_size"]<=x["item_size_max"] else "BLOCK_SIZE"
    if q=="literal":return "PASS" if named(ss["DataEmailRecordContentIPDR"]["fields"],c["name"])["literal_identifier"] else "BLOCK_LITERAL"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573EML-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert m["record"]["oid"]=="sorm-report-connection-email" and m["record"]["count_constraint"] is None
    assert [(x["name"],x["tag"],x["type"]) for x in m["choice"]["closed_branches"]]==[("mail-aaa",0,"DataEmailRecordContentAAA"),("mail-ipdr",1,"DataEmailRecordContentIPDR")]
    ipdr=m["structures"]["DataEmailRecordContentIPDR"]; aaa=m["structures"]["DataEmailRecordContentAAA"]
    assert len(ipdr["fields"])==17 and sum(not x["optional"] for x in ipdr["fields"])==10 and ipdr["tag_sequence"]==[0,10,11,12,13]
    assert named(ipdr["fields"],"attachements")["literal_identifier"] and named(ipdr["fields"],"mail-message")["published_size"] is None
    assert len(aaa["fields"])==7 and sum(not x["optional"] for x in aaa["fields"])==3 and aaa["tag_sequence"]==[10,11,12,13]
    assert m["enums"]["EmailEvent"]=={"email-send":1,"email-receive":2,"email-download":3,"email-logon-attempt":4,"email-logon":5,"email-logon-failure":6,"email-logoff":7,"email-partial-download":8}
    for n in ["EmailReceivers","EmailServers"]:
        x=m["structures"][n]["fields"][0];assert x["item_size_min"]==1 and x["item_size_max"]==512 and x["count_constraint"] is None
    cases=f["cases"];assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573EML-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures:print(*failures,sep="\n");raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 email IPDR/AAA; 64 rules, 18 evidence nodes, 17 IPDR fields, 7 AAA fields, 64 cases")
if __name__=="__main__":main()
