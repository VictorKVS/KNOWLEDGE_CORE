#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-abonents-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-abonents-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)
def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REQUESTED_ABONENTS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="module": return "PASS" if (m["module"]["name"],m["module"]["tagging"])==(c["name"],c["tagging"]) else "BLOCK_MODULE"
    if q=="export": return "PASS" if c["name"] in m["module"]["exports"] else "BLOCK_EXPORT"
    if q=="import": return "PASS" if any(x["name"]==c["name"] and x["from"]==c["from"] for x in m["module"]["imports"]) else "BLOCK_IMPORT"
    if q=="request": return "PASS" if (m["request"]["name"],len(m["request"]["fields"]))==(c["name"],c["count"]) else "BLOCK_REQUEST"
    if q=="request-field":
        x=named(m["request"]["fields"],c["name"]); return "PASS_REQUIRED" if x and not x["optional"] and (x["type"],x["selector"])==(c["type"],c["selector"]) else "BLOCK_FIELD"
    if q=="registry": return "PASS" if (m["registry"]["name"],m["registry"]["variant_count"])==(c["name"],c["count"]) else "BLOCK_REGISTRY"
    if q=="variant":
        x=named(m["registry"]["variants"],c["name"]); return "PASS" if x and (x["oid"],x["record_type"])==(c["oid"],c["record"]) else "BLOCK_VARIANT"
    if q=="structure":
        s=m["structures"].get(c["name"])
        if not s: return "BLOCK_STRUCTURE"
        fs=s["fields"]; return "PASS" if (len(fs),sum(x["optional"] is True for x in fs),sum(x["optional"] is None for x in fs))==(c["count"],c["explicit_optional"],c["ambiguous"]) else "BLOCK_STRUCTURE"
    if q=="field":
        x=named(m["structures"][c["structure"]]["fields"],c["name"])
        if not x or (x["tag"],x["type"],x["optional"])!=(c["tag"],c["type"],c["optional"]): return "BLOCK_FIELD"
        if "min" in c and x.get("size")!={"min":c["min"],"max":c["max"]}: return "BLOCK_FIELD"
        if "exact" in c and x.get("size")!={"exact":c["exact"]}: return "BLOCK_FIELD"
        if "range_min" in c and x.get("range")!={"min":c["range_min"],"max":c["range_max"]}: return "BLOCK_FIELD"
        if not any(k in c for k in ("min","exact","range_min")) and ("size" in x or "range" in x): return "BLOCK_FIELD"
        return "PASS_OPTIONAL"
    if q=="ambiguous-field":
        x=named(m["structures"][c["structure"]]["fields"],c["name"]); return "PENDING_PRIMARY_PDF" if x and x["tag"]==c["tag"] and x["raw_type_token"]==c["raw"] and x["optional"] is None else "BLOCK_FIELD"
    if q=="tags": return "PASS" if [x["tag"] for x in m["structures"][c["structure"]]["fields"]]==c["values"] else "BLOCK_TAGS"
    if q=="literal": return "PASS_LITERAL" if c["value"] in m["module"]["rendered_anomalies"] else "BLOCK_LITERAL"
    if q=="empty":
        v=m["structures"][c["structure"]]["syntactically_empty_allowed"]
        return "SYNTACTICALLY_ALLOWED" if v is True else v
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573RA-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(m["module"]["imports"])==4 and len(m["registry"]["variants"])==2
    expected={"RequestedPerson":(11,11,0),"RequestedPassport":(3,3,0),"RequestedOrganization":(9,8,1)}
    for n,counts in expected.items():
        fs=m["structures"][n]["fields"]; assert (len(fs),sum(x["optional"] is True for x in fs),sum(x["optional"] is None for x in fs))==counts
    assert [x["tag"] for x in m["structures"]["RequestedPerson"]["fields"]]==[0,1,2,3,4,6,7,8,9,10,11]
    assert named(m["structures"]["RequestedOrganization"]["fields"],"address")["raw_type_token"]=="RequestedAddressOPTIONAL"
    assert named(m["structures"]["RequestedPassport"]["fields"],"doc-type-id")["range"]=={"min":0,"max":65535}
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573RA-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 RequestedAbonents; 64 rules, 18 evidence nodes, 2 variants, 25 fields, 64 cases")
if __name__=="__main__": main()
