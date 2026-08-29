#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-file-terminal-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-file-terminal-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)
def evaluate(c,m):
    q=c["query"]; ss=m["structures"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_FILE_TERMINAL_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="record":
        x=next((x for x in m["records"] if x["name"]==c["name"]),None)
        return "PASS" if x and x["oid"]==c["oid"] and x["element_type"]==c["element"] and x["data_kind"]=="SEQUENCE OF" else "BLOCK_RECORD"
    if q=="semantic":return "NOT_SPECIFIED"
    if q=="structure-count":
        x=ss[c["structure"]]
        return "PASS" if len(x["fields"])==c["count"] and x["clear_required_count"]==c["required"] and x["clear_optional_count"]==c["optional"] and x["ambiguous_requiredness_count"]==c["ambiguous"] else "BLOCK_FIELD_CONTRACT"
    if q=="field":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if not x:return "BLOCK_UNKNOWN_FIELD"
        if x["tag"]!=c["tag"]:return "BLOCK_TAG"
        if x["optional"] is None:return "PENDING_REQUIREDNESS"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="rendered-token":
        x=named(ss[c["structure"]]["fields"],c["name"]);return "PASS_LITERAL" if x["rendered_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="rendered-comment":return "PASS_LITERAL" if ss[c["structure"]]["rendered_comment_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="boundary":
        x=named(ss[c["structure"]]["fields"],c["name"])
        if "value_min" in x:return "PASS" if x["value_min"]<=c["value"]<=x["value_max"] else "BLOCK_RANGE"
        return "PASS" if x["size_min"]<=c["value"]<=x["size_max"] else "BLOCK_SIZE"
    if q=="tag-sequence":return "PASS" if ss[c["structure"]]["tag_sequence"]==c["value"] else "BLOCK_TAG_SEQUENCE"
    if q=="tag":return "BLOCK_UNASSIGNED_TAG" if any(a<=c["value"]<=b for a,b in ss[c["structure"]]["unassigned_tag_intervals"]) else "PASS_ASSIGNED_TAG"
    if q=="enum-field":
        x=named(ss[c["structure"]]["fields"],c["name"]);return "PASS" if x["closed_values"].get(c["label"])==c["value"] else "BLOCK_ENUM"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573FTT-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert [(x["name"],x["oid"],x["element_type"]) for x in m["records"]]==[("dataFileTransferRecord","sorm-report-connection-file-transfer","DataFileTransferRecordContent"),("dataTermAccessRecord","sorm-report-connection-term-access","DataTermAccessRecordContent")]
    file= m["structures"]["DataFileTransferRecordContent"]; term=m["structures"]["DataTermAccessRecordContent"]
    assert (len(file["fields"]),file["clear_required_count"],file["clear_optional_count"],file["ambiguous_requiredness_count"])==(12,7,4,1)
    ambiguous=named(file["fields"],"file-server-type"); assert ambiguous["optional"] is None and ambiguous["type"]=="PENDING_PRIMARY_PDF" and ambiguous["rendered_token"]=="BOOLEANOPTIONAL"
    assert file["tag_sequence"]==[0,10,11,12] and file["unassigned_tag_intervals"]==[[1,9]]
    assert (len(term["fields"]),term["clear_required_count"],term["clear_optional_count"],term["ambiguous_requiredness_count"])==(9,3,6,0)
    assert named(term["fields"],"term-protocol")["closed_values"]=={"telnet":0,"ssh":1,"scp":2}
    assert term["tag_sequence"]==[0,10,11,12,13] and term["unassigned_tag_intervals"]==[[1,9]] and term["rendered_comment_token"]=="PDR-соединения"
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573FTT-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures:print(*failures,sep="\n");raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 file-transfer and terminal-access; 64 rules, 18 evidence nodes, 12+9 fields, 64 cases")
if __name__=="__main__":main()
