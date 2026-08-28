#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-abonents-core-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-abonents-core-regression-v1.json")

def named(items, name):
    return next((item for item in items if item["name"] == name), None)

def evaluate(case, model):
    query = case["query"]
    if query == "temporal":
        observed = date.fromisoformat(case["date"])
        if observed < date(2024, 3, 1):
            return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTS_ABONENTS_VERSION" if observed < date(2030, 3, 1) else "EXPIRED_ROUTE"
    if query == "export":
        return "PASS" if case["name"] in model["module"]["exports"] else "BLOCK_NOT_EXPORTED"
    if query == "open-type":
        fields = model["open_type"]["fields"]
        ok = all(not item["optional"] for item in fields) and model["open_type"]["id_data_binding_required"]
        return "PASS" if ok == (case["id_required"] and case["data_required"] and case["binding_required"]) else "BLOCK_OPEN_TYPE_CONTRACT"
    if query == "variant":
        item = named(model["variants"], case["name"])
        if item is None:
            return "BLOCK_UNKNOWN_VARIANT"
        return "PASS" if item["oid"] == case["oid"] and item["data_type"] == case["data_type"] else "BLOCK_VARIANT_BINDING_MISMATCH"
    if query == "field":
        item = named(model["types"][case["type"]]["fields"], case["name"])
        if item is None:
            return "BLOCK_UNKNOWN_FIELD"
        if item.get("tag") != case["tag"]:
            return "BLOCK_TAG_MISMATCH"
        return "PASS_OPTIONAL" if item["optional"] else "PASS_REQUIRED"
    if query == "boundary-field":
        item = named(model["types"][case["type"]]["fields"], case["name"])
        if "size_min" in item:
            return "PASS" if item["size_min"] <= case["value"] <= item["size_max"] else "BLOCK_SIZE"
        return "PASS" if item["value_min"] <= case["value"] <= item["value_max"] else "BLOCK_RANGE"
    if query == "enum":
        item = named(model["types"][case["type"]]["values"], case["name"])
        return "PASS" if item and item["value"] == case["value"] else "BLOCK_UNKNOWN_ENUM"
    if query == "sequence-of":
        item = model["types"][case["type"]]
        return "PASS" if item["kind"] == "SEQUENCE OF" and item["element_type"] == case["element_type"] else "BLOCK_TYPE_MISMATCH"
    if query == "alias":
        item = model["types"][case["type"]]
        return "PASS" if item["kind"] == "ALIAS" and item["target"] == case["target"] else "BLOCK_ALIAS_MISMATCH"
    if query == "syntax":
        return "PENDING_PRIMARY_PDF"
    if query == "semantic":
        if case["target"] == "empty-line-data":
            return "PASS_ASN1_SYNTAX_ONLY_BUSINESS_MEANING_UNSPECIFIED"
        return "NOT_SPECIFIED"
    raise AssertionError(query)

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules = model["atomic_rules"]
    evidence = model["evidence_model"]
    types = model["types"]
    assert len(rules) == len({item["id"] for item in rules}) == 64
    assert [item["id"] for item in rules] == [f"MK573RA-R{i:03d}" for i in range(1, 65)]
    assert len(evidence) == len({item["id"] for item in evidence}) == 18
    assert [rule for node in evidence for rule in node["proves"]] == [item["id"] for item in rules]
    assert model["module"]["exports"] == ["AbonentsReport"]
    assert model["module"]["rendered_import_module"] == "Networkidentifiers"
    assert [(item["name"], item["oid"], item["data_type"]) for item in model["variants"]] == [
        ("reportAbonent", "sorm-report-abonent-abonent", "SEQUENCE OF AbonentsRecord"),
        ("reportService", "sorm-report-abonent-service", "SEQUENCE OF AbonentService"),
    ]
    abonent = types["AbonentsRecord"]["fields"]
    assert len(abonent) == 16
    assert sum(not item["optional"] for item in abonent) == 8
    assert [(item["name"], item["tag"]) for item in abonent if item["optional"]] == [
        ("attach",0),("detach",1),("services",3),("line-data",4),("standard",5),("addresses",6),("last-ip",8),("last-ip-date",9)
    ]
    assert types["AbonentsRecord"]["unassigned_optional_tags"] == [2, 7]
    assert types["ActiveServices"]["element_type"] == "AbonentService" and types["ActiveServices"]["count_constraint"] is None
    assert [(item["name"], item["value"]) for item in types["ActiveStatus"]["values"]] == [("active",0),("not-active",1)]
    lines = types["LineData"]["fields"]
    assert len(lines) == 5 and all(item["optional"] for item in lines)
    assert [item["tag"] for item in lines] == [0,1,2,3,4]
    assert all((item["size_min"], item["size_max"]) == (1,128) for item in lines)
    assert types["Standard"] == {"kind":"ALIAS","target":"NetworkType"}
    service = types["AbonentService"]["fields"]
    assert len(service) == 7 and sum(not item["optional"] for item in service) == 5
    assert (named(service,"service-id")["value_min"], named(service,"service-id")["value_max"]) == (0,4294967295)
    assert len(fixtures["cases"]) == len({item["id"] for item in fixtures["cases"]}) == 64
    assert [item["id"] for item in fixtures["cases"]] == [f"MK573RA-T{i:03d}" for i in range(1,65)]
    failures = [(case["id"], case["expected"], evaluate(case, model)) for case in fixtures["cases"] if evaluate(case, model) != case["expected"]]
    if failures:
        print(*failures, sep="\n")
        raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"] and not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsAbonents core; 64 rules, 18 evidence nodes, 2 report variants, 16 abonent fields, 7 service fields, 64 cases")

if __name__ == "__main__":
    main()
