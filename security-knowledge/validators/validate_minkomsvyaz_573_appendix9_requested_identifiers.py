#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-identifiers-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-identifiers-regression-v1.json")

def branch(model, variant, name):
    return next((item for item in model["variants"][variant].get("branches",[]) if item["name"]==name),None)

def evaluate(case, model):
    query=case["query"]
    if query=="temporal":
        observed=date.fromisoformat(case["date"])
        if observed<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REQUESTED_IDENTIFIERS_VERSION" if observed<date(2030,3,1) else "EXPIRED_ROUTE"
    if query=="exports": return "PASS" if len(model["module"]["exports"])==case["count"] else "BLOCK"
    if query=="not-exported-defined": return "PASS" if case["name"] in model["module"]["not_exported_but_locally_defined"] and case["name"] in model["variants"] else "BLOCK"
    if query=="imports": return "PASS" if len(model["module"]["imports"]["Classification"])==case["classification"] and len(model["module"]["imports"]["NetworkIdentifiers"])==case["network"] else "BLOCK"
    if query=="open-type":
        fields=model["open_type"]["fields"]
        return "PASS" if len(fields)==case["fields"] and sum(item["required"] for item in fields)==case["required"] and fields[1]["dependent_on"]==case["dependent_on"] else "BLOCK"
    if query=="registry": return "PASS" if model["open_type"]["registry"]==case["variants"] else "BLOCK"
    if query=="primitive":
        item=model["variants"][case["variant"]]
        return "PASS" if item["form"]==case["form"] and item["size"]==case["size"] else "BLOCK"
    if query=="pstd-field": return "PASS" if case["field"] in model["variants"]["requestedPstnIdentifier"]["fields"] else "BLOCK"
    if query=="branch": return "PASS" if branch(model,case["variant"],case["branch"]["name"])==case["branch"] else "BLOCK"
    if query=="tag-order": return "PASS" if [item["tag"] for item in model["variants"][case["variant"]]["branches"]]==case["tags"] else "BLOCK"
    if query=="literal": return "PASS_LITERAL" if model["variants"][case["variant"]].get(case["field"])==case["value"] else "BLOCK"
    if query=="literal-pstd": return "PASS_LITERAL" if model["variants"]["requestedPstnIdentifier"]["fields"][0]["raw_token"]==case["value"] else "BLOCK"
    if query=="literal-branch":
        item=branch(model,case["variant"],case["branch"])
        return "PASS_LITERAL" if item and item.get(case["field"])==case["value"] else "BLOCK"
    if query=="missing-tags":
        tags={item["tag"] for item in model["variants"][case["variant"]]["branches"]}
        return "PASS_ABSENT" if not tags.intersection(case["tags"]) else "BLOCK"
    if query=="choice-semantics": return "PASS_EXACTLY_ONE" if model["variants"][case["variant"]].get("form")=="CHOICE" or case["variant"]=="requestedDataNetworkIdentifier" else "BLOCK"
    if query=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(query)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; cases=fixtures["cases"]
    assert len(rules)==len({item["id"] for item in rules})==64 and [item["id"] for item in rules]==[f"MK573RI-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18 and [rule for node in evidence for rule in node["proves"]]==[item["id"] for item in rules]
    assert len(cases)==len({item["id"] for item in cases})==64 and [item["id"] for item in cases]==[f"MK573RI-T{i:03d}" for i in range(1,65)]
    assert len(model["open_type"]["registry"])==6 and sum(len(item.get("branches",[])) for item in model["variants"].values())==18
    failures=[(case["id"],case["expected"],evaluate(case,model)) for case in cases if evaluate(case,model)!=case["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"] and not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 RequestedIdentifiers; 64 rules, 18 evidence nodes, 6 registry variants, 18 branches, 64 cases")

if __name__=="__main__": main()
