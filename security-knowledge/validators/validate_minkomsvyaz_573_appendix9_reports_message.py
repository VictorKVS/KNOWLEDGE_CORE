#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-message-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-message-regression-v1.json")

def named(items, name):
    return next((item for item in items if item["name"] == name), None)

def evaluate(case, model):
    query = case["query"]
    types = model["types"]
    if query == "temporal":
        observed = date.fromisoformat(case["date"])
        if observed < date(2024, 3, 1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTS_VERSION" if observed < date(2030, 3, 1) else "EXPIRED_ROUTE"
    if query == "export":
        return "PASS" if case["name"] in model["module"]["exports"] else "BLOCK_NOT_EXPORTED"
    if query == "message-oid":
        return "PASS" if case["value"] == model["report_message"]["oid"] else "BLOCK_OID_MISMATCH"
    if query == "message-choice":
        item = named(model["report_message"]["data_choice"], case["name"])
        return "PASS" if item and item["tag"] == case["tag"] and item["type"] == case["type"] else "BLOCK_UNKNOWN_CHOICE"
    if query == "field":
        item = named(types[case["type"]]["fields"], case["name"])
        if item is None: return "BLOCK_UNKNOWN_FIELD"
        return "PASS_OPTIONAL" if item["optional"] else "PASS_REQUIRED"
    if query == "field-count":
        fields = types[case["type"]]["fields"]
        return "PASS" if len(fields) == case["count"] and sum(not x["optional"] for x in fields) == case["required"] else "BLOCK_FIELD_CONTRACT"
    if query == "integer":
        item = named(types[case["type"]]["fields"], case["name"])
        return "PASS_PUBLISHED_UNCONSTRAINED_INTEGER" if item and item["type"] == "INTEGER" and item.get("published_range") is None else "BLOCK_RANGE"
    if query == "boundary-field":
        item = named(types[case["type"]]["fields"], case["name"])
        return "PASS" if item["size_min"] <= case["value"] <= item["size_max"] else "BLOCK_SIZE"
    if query == "syntax": return "PENDING_PRIMARY_PDF"
    if query == "semantic": return "NOT_SPECIFIED"
    if query == "report-data":
        item = named(types["ReportDataBlock"]["branches"], case["name"])
        return "PASS" if item and item["tag"] == case["tag"] and item["type"] == case["type"] else "BLOCK_UNKNOWN_BRANCH"
    if query == "report-data-tag":
        return "BLOCK_UNASSIGNED_TAG" if case["tag"] in types["ReportDataBlock"]["unassigned_tags"] else "PASS_ASSIGNED_TAG"
    if query == "tag-sequence":
        return "PASS" if case["value"] == [x["tag"] for x in types["ReportDataBlock"]["branches"]] else "BLOCK_TAG_SEQUENCE"
    if query == "literal":
        return "PASS_LITERAL" if named(types["ReportDataBlock"]["branches"], case["name"]) else "BLOCK_NORMALIZED_ALIAS"
    if query == "import":
        return "PASS" if case["type"] in model["module"]["imports"].get(case["module"], []) else "BLOCK_IMPORT_MISMATCH"
    raise AssertionError(query)

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules, evidence, types = model["atomic_rules"], model["evidence_model"], model["types"]
    assert len(rules) == len({x["id"] for x in rules}) == 64
    assert [x["id"] for x in rules] == [f"MK573RPT-R{i:03d}" for i in range(1, 65)]
    assert len(evidence) == len({x["id"] for x in evidence}) == 18
    assert [rule for node in evidence for rule in node["proves"]] == [x["id"] for x in rules]
    assert model["module"]["exports"] == ["reportMessage", "Acknowledgement"]
    assert model["module"]["imports"] == {
        "Classification":["TAGGED","sorm-message-report"], "Sorm":["Message","MessageID","DateAndTime"],
        "Tasks":["TaskID"], "Dictionaries":["DictionaryReport"], "ReportsConnections":["ConnectionsReport"],
        "ReportsLocations":["LocationReport"], "ReportsPayments":["PaymentsReport"], "ReportsPresense":["PresenseReport"],
        "ReportsNonFormalized":["NonFormalizedReport"], "ReportsAbonents":["AbonentsReport"], "ReportsDataContent":["DataContentReport"]}
    assert model["report_message"]["oid"] == "sorm-message-report"
    assert [(x["name"], x["type"], x["tag"]) for x in model["report_message"]["data_choice"]] == [("report","Report",0),("ack","Acknowledgement",1)]
    report = types["Report"]["fields"]
    assert [(x["name"], x["type"]) for x in report] == [("request-id","MessageID"),("task-id","TaskID"),("total-blocks-number","INTEGER"),("block-number","INTEGER"),("report-block","ReportDataBlock")]
    assert len(report) == 5 and all(not x["optional"] for x in report)
    assert named(report, "total-blocks-number")["published_range"] is None and named(report, "block-number")["published_range"] is None
    ack = types["Acknowledgement"]["fields"]
    assert [(x["name"], x["type"], x["optional"]) for x in ack] == [("successful","BOOLEAN",False),("broken-record","INTEGER",True),("error-description","UTF8String",True)]
    assert named(ack, "broken-record")["rendered_token"] == "INTEGEROPTIONAL" and named(ack, "broken-record")["published_range"] is None
    assert (named(ack, "error-description")["size_min"], named(ack, "error-description")["size_max"]) == (1, 1024)
    branches = types["ReportDataBlock"]["branches"]
    assert [(x["name"], x["type"], x["tag"]) for x in branches] == [("dictionary","DictionaryReport",0),("abonents","AbonentsReport",1),("connections","ConnectionsReport",2),("locations","LocationReport",3),("payments","PaymentsReport",4),("presense","PresenseReport",6),("nonFormalized","NonFormalizedReport",7),("data-content","DataContentReport",10)]
    assert types["ReportDataBlock"]["unassigned_tags"] == [5,8,9]
    cases = fixtures["cases"]
    assert len(cases) == len({x["id"] for x in cases}) == 64
    assert [x["id"] for x in cases] == [f"MK573RPT-T{i:03d}" for i in range(1, 65)]
    failures = [(c["id"], c["expected"], evaluate(c, model)) for c in cases if evaluate(c, model) != c["expected"]]
    if failures:
        print(*failures, sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"] and not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 Reports.asn; 64 rules, 18 evidence nodes, 2 message choices, 5 report fields, 3 acknowledgement fields, 8 sparse report-data branches, 64 cases")

if __name__ == "__main__": main()
