#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-core-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-tasks-core-regression-v1.json")

def field(model,response,name):
    return next(x for x in model["response_types"][response]["fields"] if x["name"]==name)

def evaluate(case,model):
    q=case["query"]
    if q=="temporal":
        d=date.fromisoformat(case["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_TASKS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="exports-count": return "PASS" if len(model["module"]["exports"])==case["value"] else "BLOCK"
    if q=="exports": return "PASS" if model["module"]["exports"]==case["value"] else "BLOCK"
    if q=="imports-count": return "PASS" if sum(len(x) for x in model["module"]["imports"].values())==case["value"] else "BLOCK"
    if q=="message-count": return "PASS" if len(model["task_message"]["branches"])==case["value"] else "BLOCK"
    if q=="message-tags": return "PASS" if [x["tag"] for x in model["task_message"]["branches"]]==case["value"] else "BLOCK"
    if q=="message-branch": return "PASS" if case["value"] in model["task_message"]["branches"] else "BLOCK"
    if q=="rendered-message-type":
        branch=next(x for x in model["task_message"]["branches"] if x["name"]==case["name"])
        return "PASS_LITERAL" if branch["rendered_type"]==case["value"] else "BLOCK"
    if q=="request-form": return "PASS" if model["request_types"][case["name"]]["form"]==case["value"] else "BLOCK"
    if q=="request-alias": return "PASS" if model["request_types"][case["name"]]["type"]==case["value"] else "BLOCK"
    if q=="rendered-request-definition": return "PASS_LITERAL" if model["request_types"][case["name"]]["rendered_definition"]==case["value"] else "BLOCK"
    if q=="create-fields-count": return "PASS" if len(model["request_types"]["CreateTaskRequest"]["fields"])==case["value"] else "BLOCK"
    if q=="create-field-tags": return "PASS" if [x["tag"] for x in model["request_types"]["CreateTaskRequest"]["fields"]]==case["value"] else "BLOCK"
    if q=="report-limit-range": return "PASS" if model["request_types"]["CreateTaskRequest"]["fields"][2]["range"]==case["value"] else "BLOCK"
    if q=="create-task-count": return "PASS" if len(model["request_types"]["CreateTaskRequest"]["task_branches"])==case["value"] else "BLOCK"
    if q=="create-task-tags": return "PASS" if [x["tag"] for x in model["request_types"]["CreateTaskRequest"]["task_branches"]]==case["value"] else "BLOCK"
    if q=="create-task-branch": return "PASS" if case["value"] in model["request_types"]["CreateTaskRequest"]["task_branches"] else "BLOCK"
    if q=="response-form": return "PASS" if model["response_types"][case["name"]]["form"]==case["value"] else "BLOCK"
    if q=="response-cardinality": return model["response_types"][case["name"]]["cardinality"]
    if q=="response-fields-count": return "PASS" if len(model["response_types"][case["name"]]["fields"])==case["value"] else "BLOCK"
    if q=="task-result-values": return "PASS" if [x["value"] for x in model["response_types"]["TaskResult"]["result_values"]]==case["value"] else "BLOCK"
    if q=="report-records-range": return "PASS" if field(model,"TaskResult","report-records-number")["range"]==case["value"] else "BLOCK"
    if q=="literal-task-result-name": return "PASS_LITERAL" if field(model,"TaskResult",case["value"])["name"]==case["value"] else "BLOCK"
    if q=="literal-task-result-type": return "PASS_LITERAL" if field(model,"TaskResult","report-limit-exeeded")["rendered_type"]==case["value"] else "BLOCK"
    if q=="error-description-size": return "PASS" if field(model,"TaskResult","error-description")["size"]==case["value"] else "BLOCK"
    if q=="data-blocks-number-range": return "PASS" if field(model,"DataLoadResponse","data-blocks-number")["range"]==case["value"] else "BLOCK"
    if q=="data-blocks-available-range": return "PASS" if field(model,"DataInterruptResponse","data-blocks-available")["range"]==case["value"] else "BLOCK"
    if q=="task-id-range": return "PASS" if model["base_types"]["TaskID"]["range"]==case["value"] else "BLOCK"
    if q=="data-content-size": return "PASS" if model["base_types"]["DataContentID"]["size"]==case["value"] else "BLOCK"
    if q=="logical-values": return "PASS" if [x["value"] for x in model["base_types"]["LogicalOperation"]["values"]]==case["value"] else "BLOCK"
    if q=="semantic": return "NOT_SPECIFIED"
    if q=="rendered-anomalies-count": return "PASS" if len(model["rendered_anomalies"])==case["value"] else "BLOCK"
    raise AssertionError(q)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; cases=fixtures["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573TC-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18
    assert [r for node in evidence for r in node["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573TC-T{i:03d}" for i in range(1,65)]
    assert len(model["task_message"]["branches"])==12
    assert len(model["request_types"]["CreateTaskRequest"]["task_branches"])==7
    assert len(model["response_types"])==7
    failures=[(c["id"],c["expected"],evaluate(c,model)) for c in cases if evaluate(c,model)!=c["expected"]]
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"]
    assert not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 Tasks core; 64 rules, 18 evidence nodes, 12 messages, 7 task variants, 64 cases")

if __name__=="__main__": main()
