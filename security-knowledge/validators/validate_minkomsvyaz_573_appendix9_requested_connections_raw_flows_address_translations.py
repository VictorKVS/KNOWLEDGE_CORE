#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-connections-raw-flows-address-translations-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-connections-raw-flows-address-translations-regression-v1.json")

def branch(model, object_name, branch_name):
    return next((item for item in model["objects"][object_name]["branches"] if item["name"]==branch_name),None)

def evaluate(case, model):
    query=case["query"]
    if query=="temporal":
        observed=date.fromisoformat(case["date"])
        if observed<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REQUESTED_CONNECTIONS_VERSION" if observed<date(2030,3,1) else "EXPIRED_ROUTE"
    if query=="object-count": return "PASS" if len(model["objects"])==case["count"] else "BLOCK"
    if query=="object":
        obj=model["objects"].get(case["name"])
        return "PASS" if obj and obj["oid"]==case["oid"] and len(obj["branches"])==case["count"] else "BLOCK"
    if query=="branch": return "PASS" if branch(model,case["object"],case["branch"]["name"])==case["branch"] else "BLOCK"
    if query=="tag-order": return "PASS" if [item["tag"] for item in model["objects"][case["object"]]["branches"]]==case["tags"] else "BLOCK"
    if query=="enum":
        item=branch(model,case["object"],case["branch"])
        return "PASS_CLOSED" if item and item.get("closed") is True and item.get("values")==case["values"] else "BLOCK"
    if query=="zero-lower-bound":
        item=branch(model,case["object"],case["branch"])
        return "PASS_ZERO_ALLOWED" if item and item.get("size",{}).get("min")==0 else "BLOCK"
    if query=="missing-tags":
        tags={item["tag"] for item in model["objects"][case["object"]]["branches"]}
        return "PASS_ABSENT" if not tags.intersection(case["tags"]) else "BLOCK"
    if query=="choice-semantics": return "PASS_EXACTLY_ONE" if model["objects"][case["object"]]["data_form"]=="DATA CHOICE" and model["branch_summary"]["choice_semantics"]=="EXACTLY_ONE_ALTERNATIVE_PER_CHOICE_VALUE" else "BLOCK"
    if query=="rendered-reference":
        item=branch(model,case["object"],case["branch"])
        return "PASS_LITERAL" if item and item.get("rendered_reference")==case["reference"] else "BLOCK"
    if query=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(query)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; cases=fixtures["cases"]
    assert len(rules)==len({item["id"] for item in rules})==64
    assert [item["id"] for item in rules]==[f"MK573RCRA-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18 and [rule for node in evidence for rule in node["proves"]]==[item["id"] for item in rules]
    assert len(cases)==len({item["id"] for item in cases})==64
    assert [item["id"] for item in cases]==[f"MK573RCRA-T{i:03d}" for i in range(1,65)]
    assert [len(model["objects"][name]["branches"]) for name in ("requestedRawFlows","requestedAddressTranslations")]==[8,6]
    assert model["verification_boundary"]["closed_enums"]==2
    failures=[(case["id"],case["expected"],evaluate(case,model)) for case in cases if evaluate(case,model)!=case["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"] and not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 RequestedConnections raw-flows/address-translations; 64 rules, 18 evidence nodes, 14 branches, 2 closed enums, 64 cases")

if __name__=="__main__": main()
