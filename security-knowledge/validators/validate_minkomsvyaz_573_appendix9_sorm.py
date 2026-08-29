#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-sorm-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-sorm-regression-v1.json")

def by_name(items,name):
    return next((x for x in items if x.get("name")==name),None)

def evaluate(case,model):
    q=case["query"]
    if q=="temporal":
        d=date.fromisoformat(case["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_SORM_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if model["module"]["exports"]==case["value"] else "BLOCK"
    if q=="imports": return "PASS" if model["module"]["imports"]==case["value"] else "BLOCK"
    if q=="version-base": return "PASS" if model["version"]["type_alias"]["base"]==case["value"] else "BLOCK"
    if q=="version-literal": return "PASS_LITERAL" if model["version"]["constant"]["value"]==case["value"] else "BLOCK"
    if q=="message-form": return "PASS" if model["message"]["form"]==case["value"] else "BLOCK"
    if q=="message-field": return "PASS" if case["value"] in model["message"]["fields"] else "BLOCK"
    if q=="message-counts": return "PASS" if model["message"]["required_fields"]==case["required"] and model["message"]["optional_fields"]==case["optional"] else "BLOCK"
    if q=="operator-size": return "PASS" if by_name(model["message"]["fields"],"operator-name")["size"]==case["value"] else "BLOCK"
    if q=="id-registry": return "PASS" if by_name(model["message"]["fields"],"id")["registry"]==case["value"] else "BLOCK"
    if q=="data-dependent": return "PASS" if by_name(model["message"]["fields"],"data")["dependent_on"]==case["value"] else "BLOCK"
    if q=="literal-registry": return "PASS_LITERAL" if model["registry"].get(case["field"])==case["value"] else "BLOCK"
    if q=="registry-count": return "PASS" if len(model["registry"]["variants"])==case["value"] else "BLOCK"
    if q=="registry-variant": return "PASS" if case["value"] in model["registry"]["variants"] else "BLOCK"
    if q=="message-id-range": return "PASS" if model["common_types"]["MessageID"]["range"]==case["value"] else "BLOCK"
    if q=="date-base": return "PASS" if model["common_types"]["DateAndTime"]["base"]==case["value"] else "BLOCK"
    if q=="find-form": return "PASS" if model["common_types"]["FindRange"]["form"]==case["value"] else "BLOCK"
    if q=="find-field": return "PASS" if case["value"] in model["common_types"]["FindRange"]["fields"] else "BLOCK"
    if q=="literal-end": return "PASS_LITERAL" if model["common_types"]["FindRange"]["fields"][1].get(case["field"])==case["value"] else "BLOCK"
    if q=="begin-optional": return "PASS" if by_name(model["common_types"]["FindRange"]["fields"],"begin-find")["required"] is False else "BLOCK"
    if q=="end-requiredness": return "PASS_PENDING" if model["common_types"]["FindRange"]["fields"][1]["requiredness"]==case["value"] else "BLOCK"
    if q=="find-tags": return "PASS" if [x["tag"] for x in model["common_types"]["FindRange"]["fields"]]==case["value"] else "BLOCK"
    if q=="find-order-rule": return "NOT_SPECIFIED"
    if q=="version-optional": return "PASS" if by_name(model["message"]["fields"],"version")["required"] is False else "BLOCK"
    if q=="required-field": return "PASS" if by_name(model["message"]["fields"],case["value"])["required"] is True else "BLOCK"
    if q=="optional-field": return "PASS" if by_name(model["message"]["fields"],case["value"])["required"] is False else "BLOCK"
    if q=="registry-semantics": return "PASS_OPEN_TYPE" if by_name(model["message"]["fields"],"data")["dependent_on"]=="@id" else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; cases=fixtures["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573SORM-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18
    assert [r for node in evidence for r in node["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573SORM-T{i:03d}" for i in range(1,65)]
    assert len(model["module"]["exports"])==4
    assert sum(len(x) for x in model["module"]["imports"].values())==8
    assert len(model["message"]["fields"])==6
    assert len(model["registry"]["variants"])==7
    failures=[(c["id"],c["expected"],evaluate(c,model)) for c in cases if evaluate(c,model)!=c["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"]
    assert not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 Sorm; 64 rules, 18 evidence nodes, 6 message fields, 7 registry variants, 64 cases")

if __name__=="__main__": main()
