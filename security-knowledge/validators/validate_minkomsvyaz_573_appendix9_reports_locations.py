#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-locations-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-locations-regression-v1.json")

def named(items,name): return next((x for x in items if x["name"]==name),None)

def evaluate(c,m):
    q=c["query"]; module=m["module"]; s=m["structures"].get(c.get("structure","ValidateLocationRecord"))
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTS_LOCATIONS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="module": return "PASS" if module["name"]==c["name"] and module["tagging"]==c["tagging"] else "BLOCK_MODULE"
    if q=="export": return "PASS" if c["name"] in module["exports"] else "BLOCK_EXPORT"
    if q=="import": return "PASS" if any(x["name"]==c["name"] and x["from"]==c["from"] for x in module["imports"]) else "BLOCK_IMPORT"
    if q=="report":
        r=m["report"]; return "PASS" if (r["name"],r["kind"],r["element_type"])==(c["name"],c["kind"],c["element"]) else "BLOCK_REPORT"
    if q=="semantic": return "NOT_SPECIFIED"
    if q=="structure-count": return "PASS" if s["rendered_entry_count"]==c["count"] and s["clear_required_count"]==c["required"] and s["clear_optional_count"]==c["optional"] and s["ambiguous_entry_count"]==c["ambiguous"] else "BLOCK_FIELD_CONTRACT"
    if q=="field":
        x=named(s["rendered_entries"],c["name"])
        if not x or x["optional"] is None: return "BLOCK_UNKNOWN_FIELD"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="ambiguous-entry": return "PENDING_PRIMARY_PDF" if sum(x["optional"] is None for x in s["rendered_entries"])==1 else "BLOCK_AMBIGUITY"
    if q=="rendered-token": return "PASS_LITERAL" if next(x for x in s["rendered_entries"] if x["optional"] is None)["rendered_token"]==c["value"] else "BLOCK_LITERAL"
    if q=="closing-brace": return "PENDING_PRIMARY_PDF" if s["closing_brace_before_end"].startswith("NOT_PRESENT") else "PASS"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573RL-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert m["module"]=={"name":"ReportsLocations","tagging":"IMPLICIT TAGS","exports":["LocationReport"],"imports":[{"name":"DateAndTime","from":"Sorm"},{"name":"TelcoID","from":"Dictionaries"},{"name":"Location","from":"Locations"},{"name":"ReportedIdentifier","from":"ReportedIdentifiers"}]}
    assert m["report"]=={"name":"LocationReport","kind":"SEQUENCE OF","element_type":"ValidateLocationRecord","count_constraint":None}
    s=m["structures"]["ValidateLocationRecord"]
    assert (s["rendered_entry_count"],s["clear_required_count"],s["clear_optional_count"],s["ambiguous_entry_count"])==(4,3,0,1)
    assert [(x["name"],x["type"]) for x in s["rendered_entries"][:3]]==[("telco-id","TelcoID"),("connection-time","DateAndTime"),("ident","ReportedIdentifier")]
    ambiguous=s["rendered_entries"][3]; assert ambiguous["optional"] is None and ambiguous["rendered_token"]=="connection-locationLocation" and ambiguous["commentary_role"]=="местоположение мобильного абонента"
    assert s["closing_brace_before_end"]=="NOT_PRESENT_IN_CONSOLIDATED_RENDERING_PENDING_PRIMARY_PDF"
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573RL-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsLocations; 64 rules, 18 evidence nodes, 3 clear fields + 1 pending rendered entry, 64 cases")

if __name__=="__main__": main()
