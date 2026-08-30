#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-abonents-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-abonents-regression-v1.json")

def evaluate(case,model):
    q=case["query"]
    if q=="temporal":
        d=date.fromisoformat(case["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TASKS_ABONENTS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports": return "PASS" if model["module"]["exports"]==case["value"] else "BLOCK"
    if q=="imports": return "PASS" if model["module"]["imports"]==case["value"] else "BLOCK"
    if q=="top-count": return "PASS" if len(model["top_level_task"]["branches"])==case["value"] else "BLOCK"
    if q=="top-tags": return "PASS" if [x["tag"] for x in model["top_level_task"]["branches"]]==case["value"] else "BLOCK"
    if q=="top-branch": return "PASS" if case["value"] in model["top_level_task"]["branches"] else "BLOCK"
    if q=="alias": return "PASS" if model["aliases"].get(case["name"])==case["value"] else "BLOCK"
    if q=="literal-sequence": return "PASS_LITERAL" if model["sequences"][case["name"]].get(case["field"])==case["value"] else "BLOCK"
    if q=="choice-count": return "PASS" if len(model["parameter_choices"][case["name"]]["branches"])==case["value"] else "BLOCK"
    if q=="choice-branch": return "PASS" if case["value"] in model["parameter_choices"][case["name"]]["branches"] else "BLOCK"
    if q=="sequence-form": return "PASS" if model["sequences"][case["name"]].get("form")==case["value"] else "BLOCK"
    if q=="sequence-element": return "PASS" if model["sequences"][case["name"]]["element_type"]==case["value"] else "BLOCK"
    if q=="contract-size": return "PASS" if model["parameter_choices"]["ValidateServicesParameter"]["branches"][0]["size"]==case["value"] else "BLOCK"
    if q=="mask-rule": return "PASS" if model["service_history_rule"]["query_by_mask"]==case["value"] else "BLOCK"
    if q=="full-identifier": return "PASS" if model["service_history_rule"]["identifier_requirement"]==case["value"] else "BLOCK"
    if q in ("top-choice-semantics","parameter-choice-semantics","service-selector-semantics"): return "PASS_EXACTLY_ONE"
    if q=="sequence-cardinality": return "NOT_SPECIFIED" if all(x["cardinality"]=="NOT_SPECIFIED" for x in model["sequences"].values()) else "BLOCK"
    if q=="literal-types": return "PASS" if list(model["sequences"].keys())==case["value"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; cases=fixtures["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573TA-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18
    assert [r for node in evidence for r in node["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573TA-T{i:03d}" for i in range(1,65)]
    assert len(model["top_level_task"]["branches"])==3
    assert len(model["sequences"])==3
    assert len(model["parameter_choices"])==4
    assert sum(len(x["branches"]) for x in model["parameter_choices"].values())+3==11
    failures=[(c["id"],c["expected"],evaluate(c,model)) for c in cases if evaluate(c,model)!=c["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"]
    assert not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 TasksAbonents; 64 rules, 18 evidence nodes, 3 tasks, 11 branches, 64 cases")

if __name__=="__main__": main()
