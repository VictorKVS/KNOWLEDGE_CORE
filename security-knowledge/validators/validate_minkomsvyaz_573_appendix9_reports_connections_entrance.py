#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-entrance-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-entrance-regression-v1.json")

def named(items,name): return next((x for x in items if x["name"]==name),None)

def evaluate(c,m):
    q=c["query"]; ss=m["structures"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_ENTRANCE_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="record":
        x=next((x for x in m["records"] if x["name"]==c["name"]),None)
        return "PASS" if x and x["oid"]==c["oid"] and x["element_type"]==c["element"] and x["data_kind"]=="SEQUENCE OF" else "BLOCK_RECORD"
    if q=="semantic": return "NOT_SPECIFIED"
    if q=="record-assignment": return "PASS_LITERAL" if m["records"][0]["rendered_assignment_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="structure-assignment": return "PASS_LITERAL" if ss[c["structure"]]["rendered_assignment_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="structure-count":
        x=ss[c["structure"]]
        return "PASS" if len(x["fields"])==c["count"] and x["clear_required_count"]==c["required"] and x["clear_optional_count"]==c["optional"] and x["ambiguous_requiredness_count"]==c["ambiguous"] else "BLOCK_FIELD_CONTRACT"
    if q=="field":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if not x: return "BLOCK_UNKNOWN_FIELD"
        if x["tag"]!=c["tag"]: return "BLOCK_TAG"
        if x["optional"] is None: return "PENDING_REQUIREDNESS"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="boundary":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if "value_min" in x: return "PASS" if x["value_min"]<=c["value"]<=x["value_max"] else "BLOCK_RANGE"
        return "PASS" if x["size_min"]<=c["value"]<=x["size_max"] else "BLOCK_SIZE"
    if q=="tag-sequence": return "PASS" if ss[c["structure"]]["tag_sequence"]==c["value"] else "BLOCK_TAG_SEQUENCE"
    if q=="rendered-token":
        x=named(ss[c["structure"]]["fields"],c["name"]); return "PASS_LITERAL" if x["rendered_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="empty-service-parameter": return "PASS_SYNTACTICALLY_POSSIBLE" if ss["EntranceServiceParameter"]["empty_sequence_syntactically_possible"] else "BLOCK_EMPTY"
    if q=="enum":
        x=m["enums"][c["name"]]["closed_values"]
        return "PASS" if x.get(c["label"])==c["value"] else "BLOCK_ENUM"
    if q=="enum-reference": return "PASS" if m["enums"][c["name"]]["enum_reference"]==c["value"] else "BLOCK_REFERENCE"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573EN-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    rec=m["records"][0]; assert (rec["name"],rec["oid"],rec["element_type"],rec["rendered_assignment_token"])==("dataEntranceRecord","sorm-report-connection-entrance","DataEntranceRecordContent","dataEntranceRecord TAGGED :: =")
    entrance=m["structures"]["DataEntranceRecordContent"]; service=m["structures"]["EntranceServiceParameter"]
    assert entrance["rendered_assignment_token"]=="DataEntranceRecordContent :: ="
    assert (len(entrance["fields"]),entrance["clear_required_count"],entrance["clear_optional_count"],entrance["ambiguous_requiredness_count"])==(10,2,7,1)
    assert entrance["tag_sequence"]==list(range(8))
    location=named(entrance["fields"],"entrance-location"); assert location["optional"] is None and location["type"]=="PENDING_PRIMARY_PDF" and location["rendered_token"]=="LocationOPTIONAL"
    assert named(entrance["fields"],"entrance-event-type")["enum_reference"]=="NetworkIdentifiers.EntranceEventType"
    assert (len(service["fields"]),service["clear_required_count"],service["clear_optional_count"],service["ambiguous_requiredness_count"])==(4,0,4,0)
    assert service["tag_sequence"]==[0,1,2,3] and service["empty_sequence_syntactically_possible"]
    assert m["enums"]["EntranceEventStatus"]["closed_values"]=={"event-failed":0,"event-succeeded":1}
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573EN-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 entrance records; 64 rules, 18 evidence nodes, 10+4 fields, 2 status values, 64 cases")

if __name__=="__main__": main()
