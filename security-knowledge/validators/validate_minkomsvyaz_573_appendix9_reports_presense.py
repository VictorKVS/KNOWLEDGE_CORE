#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-presense-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-presense-regression-v1.json")
def named(items,name): return next((x for x in items if x["name"]==name),None)

def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTS_PRESENSE_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="module": return "PASS" if (m["module"]["name"],m["module"]["tagging"])==(c["name"],c["tagging"]) else "BLOCK_MODULE"
    if q=="export": return "PASS" if c["name"] in m["module"]["exports"] else "BLOCK_EXPORT"
    if q=="import": return "PASS" if any(x["name"]==c["name"] and x["from"]==c["from"] for x in m["module"]["imports"]) else "BLOCK_IMPORT"
    if q=="report":
        r=m["report"]; return "PASS" if (r["name"],r["kind"],len(r["fields"]))==(c["name"],c["kind"],c["field_count"]) else "BLOCK_REPORT"
    if q=="report-field":
        x=named(m["report"]["fields"],c["name"]); return "PASS_REQUIRED" if x and not x["optional"] and (x["type"],x["selector"])==(c["type"],c["selector"]) else "BLOCK_FIELD"
    if q=="registry":
        r=m["registry"]; return "PASS" if (r["name"],r["class"],r["variant_count"])==(c["name"],c["class"],c["count"]) else "BLOCK_REGISTRY"
    if q=="variant":
        x=named(m["registry"]["variants"],c["name"]); return "PASS" if x and x["oid"]==c["oid"] else "BLOCK_VARIANT"
    if q=="variant-kind":
        x=named(m["registry"]["variants"],c["name"]); return "PASS" if x and x["data_kind"]==c["kind"] else "BLOCK_VARIANT_KIND"
    if q=="structure":
        s=m["structures"].get(c["name"])
        if not s: return "BLOCK_STRUCTURE"
        fs=s["fields"]; return "PASS" if (len(fs),sum(not x["optional"] for x in fs),sum(x["optional"] for x in fs))==(c["count"],c["required"],c["optional"]) else "BLOCK_STRUCTURE"
    if q=="field":
        s=m["structures"].get(c["structure"]); x=named(s["fields"],c["name"]) if s else None
        if not x or x["type"]!=c["type"] or x["optional"]!=c["optional"]: return "BLOCK_FIELD"
        if "range_min" in c and x.get("range")!={"min":c["range_min"],"max":c["range_max"]}: return "BLOCK_FIELD"
        if "range_min" not in c and "range" in x: return "BLOCK_FIELD"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    values=named(m["structures"]["ConnectionsPresenseRecord"]["fields"],"data-type")["values"]
    if q=="enum-count": return "PASS" if len(values)==c["count"] else "BLOCK_ENUM"
    if q=="enum": return "PASS" if values.get(c["name"])==c["value"] else "BLOCK_ENUM"
    if q=="literal": return "PASS_LITERAL" if c["value"] in m["module"]["rendered_anomalies"] else "BLOCK_LITERAL"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573PR-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert m["module"]["exports"]==["PresenseReport","StandardInterval"] and len(m["module"]["imports"])==12
    assert m["report"]["fields"]==[{"name":"id","type":"TAGGED.&id","object_set":"ReportedPresensesVariants","selector":None,"optional":False},{"name":"data","type":"TAGGED.&Data","object_set":"ReportedPresensesVariants","selector":"@id","optional":False}]
    variants=m["registry"]["variants"]; assert len(variants)==5 and sum(x["data_kind"]=="SEQUENCE OF" for x in variants)==3 and sum(x["data_kind"]=="UNRESOLVED_RENDERED_TOKEN" for x in variants)==2
    expected={"ConnectionsPresenseRecord":(2,2,0),"DictionaryInfo":(4,4,0),"StandardInterval":(4,3,1)}
    for n,counts in expected.items():
        fs=m["structures"][n]["fields"]; assert (len(fs),sum(not x["optional"] for x in fs),sum(x["optional"] for x in fs))==counts
    enum=named(m["structures"]["ConnectionsPresenseRecord"]["fields"],"data-type")["values"]; assert list(enum.values())==list(range(13))
    assert named(m["structures"]["DictionaryInfo"]["fields"],"count")["range"]=={"min":1,"max":4294967295}
    count=named(m["structures"]["StandardInterval"]["fields"],"count"); assert count=={"name":"count","type":"INTEGER","optional":True}
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573PR-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsPresense; 64 rules, 18 evidence nodes, 5 variants, 10 fields, 13 enum values, 64 cases")
if __name__=="__main__": main()
