#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-content-task-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-content-task-regression-v1.json")
AUDIT=Path("security-knowledge/audits/order573-appendix9-module-completeness-2026-08-30.yaml")
def evaluate(c,m,a):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TASKS_CONTENT_TASK_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="module-name": return "PASS" if m["module"]["name"]==c["value"] else "BLOCK"
    if q=="module-ordinal": return "PASS" if m["module"]["ordinal_in_appendix"]==c["value"] else "BLOCK"
    if q=="tagging": return "PASS" if m["module"]["tagging"]==c["value"] else "BLOCK"
    if q=="exports": return "PASS" if m["module"]["exports"]==c["value"] else "BLOCK"
    if q=="imports": return "PASS" if m["module"]["imports"]==c["value"] else "BLOCK"
    if q=="definition-name": return "PASS" if m["definition"]["name"]==c["value"] else "BLOCK"
    if q=="definition-form": return "PASS" if m["definition"]["form"]==c["value"] else "BLOCK"
    if q=="definition-target": return "PASS" if m["definition"]["target"]==c["value"] else "BLOCK"
    if q=="definition-target-module": return "PASS" if m["definition"]["target_module"]==c["value"] else "BLOCK"
    if q=="local-constraints": return "PASS" if m["definition"]["local_constraints"]==c["value"] else "BLOCK"
    if q=="summary": return "PASS" if m["summary"][c["key"]]==c["value"] else "BLOCK"
    if q=="guard": return "PASS" if c["value"] in m["semantic_guards"] else "BLOCK"
    if q=="audit-heading-count": return "PASS" if a["summary"]["visible_numbered_headings"]==c["value"] else "BLOCK"
    if q=="audit-mapped-count": return "PASS" if a["summary"]["mapped_headings"]==c["value"] else "BLOCK"
    if q=="audit-unmapped-count": return "PASS" if a["summary"]["unmapped_headings"]==c["value"] else "BLOCK"
    if q=="audit-package-count": return "PASS" if a["summary"]["atomic_packages"]==c["value"] else "BLOCK"
    if q=="audit-status": return "PASS" if a["summary"]["structural_status"]==c["value"] else "BLOCK"
    if q=="audit-module":
        x=next((x for x in a["modules"] if x["ordinal"]==c["ordinal"]),None)
        return "PASS" if x and x["name"]==c["name"] and x["packages"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    a=yaml.safe_load(AUDIT.read_text(encoding="utf-8"))
    cases=json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]
    rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573TCT-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573TCT-T{i:03d}" for i in range(1,65)]
    assert [x["ordinal"] for x in a["modules"]]==list(range(1,32))
    assert sum(len(x["packages"]) for x in a["modules"])==57
    failures=[(c["id"],c["expected"],evaluate(c,m,a)) for c in cases if evaluate(c,m,a)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"]
    assert not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 TasksContentTask; 64 rules, 18 evidence nodes, 64 cases; Appendix 9 visible headings 31/31 mapped to 57 packages")
if __name__=="__main__": main()
