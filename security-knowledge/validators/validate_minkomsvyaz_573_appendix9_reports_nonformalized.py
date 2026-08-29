#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-nonformalized-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-nonformalized-regression-v1.json")

def branch(items,name): return next((x for x in items if x["name"]==name),None)

def evaluate(c,m):
    q=c["query"]; module=m["module"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTS_NONFORMALIZED_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="module": return "PASS" if module["name"]==c["name"] and module["tagging"]==c["tagging"] else "BLOCK_MODULE"
    if q=="export": return "PASS" if c["name"] in module["exports"] else "BLOCK_EXPORT"
    if q=="import":
        return "PASS" if any(c["name"] in x["names"] and x["from"]==c["from"] for x in module["imports"]) else "BLOCK_IMPORT"
    if q=="rendered-import":
        x=module["imports"][1]; return "PASS_LITERAL" if x["rendered_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="import-resolution":
        x=next(x for x in module["imports"] if c["name"] in x["names"]); return x["resolution"]
    if q=="unused-import": return "PASS_VISIBLE_UNUSED" if c["name"] in m["unused_visible_imports"] else "BLOCK_UNUSED_IMPORT"
    if q=="choice-count": return "PASS" if m["report_choice"]["branch_count"]==c["count"] else "BLOCK_CHOICE_COUNT"
    if q=="branch":
        x=branch(m["report_choice"]["branches"],c["name"])
        return "PASS" if x and (x["tag"],x["type"])==(c["tag"],c["type"]) else "BLOCK_BRANCH"
    if q=="tag":
        x=branch(m["report_choice"]["branches"],c["name"])
        return "PASS" if x and x["tag"]==c["tag"] else "BLOCK_TAG"
    if q=="alias":
        x=m["aliases"].get(c["name"])
        return "PASS" if x and (x["kind"],x["element"])==(c["kind"],c["element"]) else "BLOCK_ALIAS"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573NF-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert m["module"]["name"]=="ReportsNonFormalized" and m["module"]["tagging"]=="IMPLICIT TAGS" and m["module"]["exports"]==["NonFormalizedReport"]
    assert m["module"]["imports"][0]=={"names":["EntityId","NonFormalizedEntityAttributeData"],"from":"TasksNonFormalized","resolution":"VERIFIED_RENDERED"}
    assert m["module"]["imports"][1]=={"names":["StandardInterval"],"from":"PENDING_PRIMARY_PDF","rendered_token":"FROMReports Presense","resolution":"PENDING_PRIMARY_PDF"}
    assert m["report_choice"]["name"]=="NonFormalizedReport" and m["report_choice"]["kind"]=="CHOICE" and m["report_choice"]["branch_count"]==2
    assert [(x["name"],x["tag"],x["type"]) for x in m["report_choice"]["branches"]]==[("nonformalized-report",0,"NonFormalizedRecords"),("nonformalized-presense",1,"NonFormalizedPresenseInfo")]
    assert {k:(v["kind"],v["element"],v["count_constraint"]) for k,v in m["aliases"].items()}=={
        "NonFormalizedRecords":("SEQUENCE OF","NonFormalizedRecord",None),"NonFormalizedPresenseInfo":("SEQUENCE OF","StandardInterval",None),"NonFormalizedRecord":("SEQUENCE OF","NonFormalizedEntityAttributeData",None)}
    assert m["unused_visible_imports"]==["EntityId"]
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573NF-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsNonFormalized; 64 rules, 18 evidence nodes, 2 CHOICE branches, 3 aliases, 64 cases")

if __name__=="__main__": main()
