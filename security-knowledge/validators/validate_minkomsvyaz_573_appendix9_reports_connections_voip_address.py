#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-voip-address-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-voip-address-regression-v1.json")

def named(items,name): return next((x for x in items if x["name"]==name),None)

def evaluate(c,m):
    q=c["query"]; ss=m["structures"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_VOIP_ADDRESS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="record":
        x=next((x for x in m["records"] if x["name"]==c["name"]),None)
        return "PASS" if x and x["oid"]==c["oid"] and x["element_type"]==c["element"] and x["data_kind"]=="SEQUENCE OF" else "BLOCK_RECORD"
    if q=="semantic": return "NOT_SPECIFIED"
    if q=="structure-count":
        x=ss[c["structure"]]
        return "PASS" if len(x["fields"])==c["count"] and x["clear_required_count"]==c["required"] and x["clear_optional_count"]==c["optional"] and x["ambiguous_requiredness_count"]==c["ambiguous"] else "BLOCK_FIELD_CONTRACT"
    if q=="field":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if not x: return "BLOCK_UNKNOWN_FIELD"
        if x["tag"]!=c["tag"]: return "BLOCK_TAG"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="boundary":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if "value_min" in x: return "PASS" if x["value_min"]<=c["value"]<=x["value_max"] else "BLOCK_RANGE"
        return "PASS" if x["size_min"]<=c["value"]<=x["size_max"] else "BLOCK_SIZE"
    if q=="tag-sequence": return "PASS" if ss[c["structure"]]["tag_sequence"]==c["value"] else "BLOCK_TAG_SEQUENCE"
    if q=="tag": return "BLOCK_UNASSIGNED_TAG" if any(a<=c["value"]<=b for a,b in ss[c["structure"]]["unassigned_tag_intervals"]) else "PASS_ASSIGNED_TAG"
    if q=="enum":
        x=m["enums"][c["name"]]["closed_values"]
        return "PASS" if x.get(c["label"])==c["value"] else "BLOCK_ENUM"
    if q=="rendered-assignment": return "PASS_LITERAL" if m["enums"][c["name"]]["rendered_assignment_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="enum-field":
        x=named(ss[c["structure"]]["fields"],c["name"])["closed_values"]
        return "PASS" if x.get(c["label"])==c["value"] else "BLOCK_ENUM"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573VA-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert [(x["name"],x["oid"],x["element_type"]) for x in m["records"]]==[("dataVoipRecord","sorm-report-connection-voip","DataVoipRecordContent"),("dataAddressTranslationRecord","sorm-report-connection-address-translations","DataAddressTranslationRecordContent")]
    voip=m["structures"]["DataVoipRecordContent"]; address=m["structures"]["DataAddressTranslationRecordContent"]
    assert (len(voip["fields"]),voip["clear_required_count"],voip["clear_optional_count"],voip["ambiguous_requiredness_count"])==(22,12,10,0)
    assert voip["tag_sequence"]==[0,1,2,3,4,5,10,11,12,13] and voip["unassigned_tag_intervals"]==[[6,9]]
    assert named(voip["fields"],"voip-protocol")["enum_reference"]=="NetworkIdentifiers.VoipProtocol"
    assert m["enums"]["VoIPEvent"]=={"closed_values":{"outgoing":0,"incoming":1,"unknown":2},"rendered_assignment_token":"VoIPEvent:: =","asn1_compilability":"PENDING_PRIMARY_PDF"}
    assert (len(address["fields"]),address["clear_required_count"],address["clear_optional_count"],address["ambiguous_requiredness_count"])==(8,8,0,0)
    assert named(address["fields"],"record-type")["closed_values"]=={"session-start":0,"session-end":1}
    assert named(address["fields"],"translation-type")["closed_values"]=={"static-nat":0,"dynamic-nat":1,"source-nat":2,"destination-nat":3,"pat":4}
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573VA-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 VoIP and address translation; 64 rules, 18 evidence nodes, 22+8 fields, 64 cases")

if __name__=="__main__": main()
