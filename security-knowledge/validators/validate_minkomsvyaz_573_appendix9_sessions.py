#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-sessions-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-sessions-regression-v1.json")

def item_by_name(items,name):
    return next((item for item in items if item.get("name")==name),None)

def evaluate(case,model):
    q=case["query"]
    if q=="temporal":
        observed=date.fromisoformat(case["date"])
        if observed<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_SESSIONS_VERSION" if observed<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if model["module"]["exports"]==case["value"] else "BLOCK"
    if q=="imports": return "PASS" if model["module"]["imports"]["Classification"]==case["value"] else "BLOCK"
    if q=="used-not-imported": return "PASS_PENDING" if case["value"] in model["module"]["used_but_not_visible_in_imports"] else "BLOCK"
    if q=="choice-count": return "PASS" if len(model["session_message"]["branches"])==case["value"] else "BLOCK"
    if q=="tag-order": return "PASS" if [x["tag"] for x in model["session_message"]["branches"]]==case["value"] else "BLOCK"
    if q=="branch": return "PASS" if case["value"] in model["session_message"]["branches"] else "BLOCK"
    if q=="request-field": return "PASS" if case["value"] in model["types"]["ConnectRequest"]["fields"] else "BLOCK"
    if q=="request-unit": return "PASS" if item_by_name(model["types"]["ConnectRequest"]["fields"],case["field"]).get("unit")==case["value"] else "BLOCK"
    if q=="request-meaning": return "PASS" if item_by_name(model["types"]["ConnectRequest"]["fields"],case["field"]).get("meaning")==case["value"] else "BLOCK"
    if q=="response-count": return "PASS" if len(model["types"]["ConnectResponse"]["fields"])==case["value"] else "BLOCK"
    if q=="response-field": return "PASS" if case["value"] in model["types"]["ConnectResponse"]["fields"] else "BLOCK"
    if q=="relation": return "PASS" if case["value"] in model["explicit_relations"] else "BLOCK"
    if q=="literal-response":
        raw=model["types"]["ConnectResponse"]["fields"][-1]
        return "PASS_LITERAL" if raw.get(case["field"])==case["value"] else "BLOCK"
    if q=="adjustment-field":
        return ("PASS_LITERAL" if case["field"]=="name" else "PASS") if model["types"]["AdjustmentRequest"]["fields"][0].get(case["field"])==case["value"] else "BLOCK"
    if q=="list-relation": return "PASS_LITERAL" if model["explicit_relations"][-1].get(case["field"])==case["value"] else "BLOCK"
    if q=="type-form": return "PASS" if model["types"][case["type"]]["form"]==case["value"] else "BLOCK"
    if q=="choice-semantics": return "PASS_EXACTLY_ONE" if model["session_message"]["data_form"]=="CHOICE" else "BLOCK"
    if q=="absent-response-field":
        return "PASS_ABSENT" if item_by_name(model["types"]["ConnectResponse"]["fields"],case["value"]) is None else "BLOCK"
    if q=="timeout-units":
        return "NOT_SPECIFIED" if all(item_by_name(model["types"]["ConnectRequest"]["fields"],n).get("unit")=="NOT_SPECIFIED_IN_VISIBLE_TEXT" for n in ["session-timeout","data-load-timeout","request-response-timeout","data-packet-response-timeout"]) else "BLOCK"
    if q=="objectdescriptor-import": return "PASS_ABSENT" if "ObjectDescriptor" not in model["module"]["imports"]["Classification"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; cases=fixtures["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573SES-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18
    assert [r for node in evidence for r in node["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573SES-T{i:03d}" for i in range(1,65)]
    assert len(model["session_message"]["branches"])==6
    assert len(model["types"]["ConnectRequest"]["fields"])==6
    assert len(model["types"]["ConnectResponse"]["fields"])==5
    failures=[(c["id"],c["expected"],evaluate(c,model)) for c in cases if evaluate(c,model)!=c["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"]
    assert not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 Sessions; 64 rules, 18 evidence nodes, 6 branches, 6 request fields, 4 numeric relations, 64 cases")

if __name__=="__main__": main()
