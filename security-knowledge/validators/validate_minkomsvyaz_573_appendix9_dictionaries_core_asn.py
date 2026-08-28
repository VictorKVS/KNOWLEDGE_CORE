#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-core-asn-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-core-asn-regression-v1.json")


def evaluate(case, model):
    when = date.fromisoformat(case["date"])
    if when < date(2024, 3, 1):
        return "HISTORICAL_PRE_REPLACEMENT"
    query = case["query"]
    if query == "temporal":
        return "PASS_CURRENT_MODULE_VERSION" if when < date(2030, 3, 1) else "EXPIRED_ROUTE"
    if query == "telco_id":
        return "PASS" if model["telco_id"]["minimum"] <= case["value"] <= model["telco_id"]["maximum"] else "BLOCK_RANGE"
    if query == "telco_list_count":
        if case["count"] < 0:
            return "BLOCK_INVALID_COUNT"
        return "PASS_NO_SIZE_CONSTRAINT_NO_BUSINESS_INFERENCE" if case["count"] == 0 else "PASS_NO_SIZE_CONSTRAINT"
    if query == "export":
        return "PASS_EXPORTED" if case["name"] in model["module"]["exports"] else "BLOCK_INTERNAL_NOT_EXPORTED"
    if query == "import_group":
        values = model["module"]["import_groups"].get(case["name"], [])
        return "PASS" if len(values) == case["count"] else "BLOCK_IMPORT_GROUP"
    if query == "task_oid":
        return "PASS" if case["value"] == model["dictionary_task"]["dictionaryTask"]["oid"] else "BLOCK_TASK_OID"
    if query == "task_descriptor":
        return "PASS" if case["value"] in model["dictionary_task"]["allowed_object_descriptors"] else "BLOCK_UNKNOWN_DESCRIPTOR"
    if query == "report_variant":
        variants = {item["name"]: item for item in model["dictionary_report"]["variants"]}
        if case["name"] not in variants:
            return "BLOCK_NORMALIZED_ALIAS"
        item = variants[case["name"]]
        if "oid_render_status" in item:
            return "PASS_WITH_OID_DELIMITER_PENDING"
        if case["name"] == "mobileSubscriberIdenityPlanRecords":
            return "PASS_LITERAL_IDENTY"
        if case["name"] == "signalPointCodes":
            return "PASS_LITERAL_NO_RECORDS_SUFFIX"
        return "PASS"
    if query == "phone_abonent_type":
        values = {item["name"]: item["value"] for item in model["phone_abonent_type"]["values"]}
        return "PASS" if values.get(case["name"]) == case["value"] else "BLOCK_ENUM"
    if query == "syntax_claim":
        return "BLOCK_PENDING_PRIMARY_PDF"
    raise AssertionError(query)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 40
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 15
    assert model["module"]["exports"] == ["TelcoID", "TelcoList", "DictionaryTask", "DictionaryReport", "PhoneAbonentType"]
    assert {key: len(value) for key, value in model["module"]["import_groups"].items()} == {
        "Sorm": 1, "Classification": 20, "Addresses": 1, "NetworkIdentifiers": 7, "Locations": 1
    }
    assert sum(len(value) for value in model["module"]["import_groups"].values()) == 30
    assert model["telco_id"] == {"kind": "INTEGER", "minimum": 0, "maximum": 65535}
    assert model["telco_list"]["size_constraint"] == "NOT_SPECIFIED"
    assert len(model["dictionary_task"]["fields"]) == 2
    assert all(not item["optional"] for item in model["dictionary_task"]["fields"])
    assert model["dictionary_task"]["variants"]["members"] == ["dictionaryTask"]
    descriptors = model["dictionary_task"]["allowed_object_descriptors"]
    variants = model["dictionary_report"]["variants"]
    assert len(descriptors) == len(set(descriptors)) == 18
    assert len(variants) == len({item["name"] for item in variants}) == 18
    assert {item["oid"] for item in variants} == set(descriptors)
    assert all(item["data"].startswith("SEQUENCE OF ") for item in variants)
    assert variants[-2]["name"] == "mobileSubscriberIdenityPlanRecords"
    assert variants[-1]["name"] == "signalPointCodes"
    assert [(item["name"], item["value"]) for item in model["phone_abonent_type"]["values"]] == [
        ("local", 0), ("network", 1), ("roamer", 2), ("undefined", 3)
    ]
    assert model["dictionary_report"]["declaration_token_status"].startswith("PENDING_PRIMARY_PDF")
    assert len(fixtures["cases"]) == len({item["id"] for item in fixtures["cases"]}) == 64
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 573 appendix 9 Dictionaries.asn core; 40 rules, 15 evidence nodes, 30 imports, 18 descriptors, 18 report variants, 64 cases")


if __name__ == "__main__":
    main()
