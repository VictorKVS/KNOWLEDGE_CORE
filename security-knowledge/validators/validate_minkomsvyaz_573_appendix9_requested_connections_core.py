#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-connections-core-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-connections-core-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)
def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REQUESTED_CONNECTIONS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="module": return "PASS" if (m["module"]["name"],m["module"]["tagging"])==(c["name"],c["tagging"]) else "BLOCK_MODULE"
    if q=="export": return "PASS" if c["name"] in m["module"]["exports"] else "BLOCK_EXPORT"
    if q=="import-count": return "PASS" if m["module"]["import_count"]==c["count"] else "BLOCK_IMPORTS"
    if q=="import-module": return "PASS" if len(m["module"]["imports_by_module"].get(c["name"],[]))==c["count"] else "BLOCK_IMPORTS"
    if q=="request": return "PASS" if (m["request"]["name"],len(m["request"]["fields"]))==(c["name"],c["count"]) else "BLOCK_REQUEST"
    if q=="request-field":
        x=named(m["request"]["fields"],c["name"]); return "PASS_REQUIRED" if x and not x["optional"] and (x["type"],x["selector"])==(c["type"],c["selector"]) else "BLOCK_FIELD"
    if q=="registry":
        r=m["registry"]; return "PASS" if (r["name"],r["variant_count"],r["imported_object_count"],r["local_object_count"])==(c["name"],c["count"],c["imported"],c["local"]) else "BLOCK_REGISTRY"
    if q=="variant":
        x=named(m["registry"]["variants"],c["name"]); return "PASS" if x and (x["position"],x.get("oid"))==(c["position"],c.get("oid")) and ("origin" not in c or x["origin"]==c["origin"]) else "BLOCK_VARIANT"
    if q=="data-form":
        x=named(m["registry"]["variants"],c["name"]); return "PASS_DATA_CHOICE" if x and x["data_form"]=="DATA CHOICE" else "BLOCK_DATA_FORM"
    if q=="raw-data-token":
        x=named(m["registry"]["variants"],c["name"]); return "PENDING_PRIMARY_PDF" if x and x.get("raw_data_token")==c["value"] else "BLOCK_LITERAL"
    if q=="definition-name":
        x=named(m["registry"]["variants"],c["name"]); return "PENDING_PRIMARY_PDF" if x and x.get("rendered_definition_name")==c["rendered"] else "BLOCK_LITERAL"
    if q=="pager-origin":
        x=m["registry"]["variants"][0]; return "PASS_IMPORTED_WITHOUT_LOCAL_OID" if x["origin"]=="IMPORTED_TAGGED_OBJECT" and x["oid"] is None else "BLOCK_PAGER"
    if q=="registry-order": return "PASS" if [x["position"] for x in m["registry"]["variants"]]==list(range(1,15)) else "BLOCK_ORDER"
    if q=="semantic": return "NOT_SPECIFIED"
    if q=="pending": return {"primary-pdf":m["verification_boundary"]["primary_pdf"],"official-immutable-bytes":m["verification_boundary"]["current_consolidated_official_immutable_bytes"],"independent-review":m["verification_boundary"]["independent_expert_review"]}[c["subject"]]
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573RCC-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert sum(len(x) for x in m["module"]["imports_by_module"].values())==m["module"]["import_count"]==29
    assert len(m["registry"]["variants"])==14 and [x["position"] for x in m["registry"]["variants"]]==list(range(1,15))
    assert sum(x["origin"]=="IMPORTED_TAGGED_OBJECT" for x in m["registry"]["variants"])==1
    assert sum(x.get("oid") is not None for x in m["registry"]["variants"])==13
    assert named(m["registry"]["variants"],"requestedConnectionEntrance")["raw_data_token"]=="DATACHOICE"
    assert named(m["registry"]["variants"],"requestedTermAccess")["rendered_definition_name"]=="requestedTerm Access"
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573RCC-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 RequestedConnections core; 64 rules, 18 evidence nodes, 14 variants, 64 cases")
if __name__=="__main__": main()
