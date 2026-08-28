#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-addresses-asn-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-addresses-asn-regression-v1.json")


def evaluate(case, model):
    if date.fromisoformat(case["date"]) < date(2024, 3, 1):
        return "HISTORICAL_PRE_REPLACEMENT"
    query = case["query"]
    if query == "enum":
        values = {item["name"]: item["value"] for item in model["address_type"]["values"]}
        return "PASS" if values.get(case["name"]) == case["value"] else "BLOCK_ENUM"
    if query == "reported_address":
        if not case["title"]:
            return "BLOCK_REQUIRED_TITLE"
        if not case["address_info"]:
            return "BLOCK_REQUIRED_ADDRESS_INFO"
        return "PASS"
    if query == "choice":
        if len(case["alternatives"]) != 1:
            return "BLOCK_CHOICE_CARDINALITY"
        alternative = case["alternatives"][0]
        if alternative == "struct-info":
            if case.get("struct_field_count") == 0:
                return "PASS_ASN1_EMPTY_SEQUENCE_NO_BUSINESS_SEMANTICS"
            return "PASS"
        if alternative == "unstruct-info":
            return "PASS" if 1 <= case["length"] <= 1024 else "BLOCK_SIZE"
        return "BLOCK_UNKNOWN_ALTERNATIVE"
    if query in {"reported_field", "requested_field"}:
        fields = model["reported_struct_fields"] if query == "reported_field" else model["requested_address"]["fields"]
        item = next((field for field in fields if field["name"] == case["field"]), None)
        if item is None:
            return "BLOCK_UNKNOWN_FIELD"
        return "PASS" if item["size_min"] <= case["length"] <= item["size_max"] else "BLOCK_SIZE"
    if query == "requested_empty":
        return "PASS_ASN1_EMPTY_SEQUENCE_NO_QUERY_SEMANTICS"
    if query == "sequence_count":
        return "BLOCK_INVALID_COUNT" if case["count"] < 0 else "PASS_NO_SIZE_CONSTRAINT"
    if query == "export":
        return "PASS_EXPORTED" if case["type"] in model["module"]["exports"] else "BLOCK_INTERNAL_NOT_EXPORTED"
    if query == "choice_tag":
        alternatives = {item["name"]: item["tag"] for item in model["address_info_report"]["alternatives"]}
        return "PASS" if alternatives.get(case["alternative"]) == case["tag"] else "BLOCK_TAG"
    raise AssertionError(query)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 34
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 14
    assert model["module"]["exports"] == ["AddressType", "ReportedAddresses", "ReportedAddress", "RequestedAddress"]
    assert model["module"]["imports"] == []
    assert [(item["name"], item["value"]) for item in model["address_type"]["values"]] == [
        ("registered", 0), ("postal", 1), ("invoice", 2), ("device-location", 3), ("reserved", 4)
    ]
    assert model["reported_addresses"]["size_constraint"] == "NOT_SPECIFIED"
    assert all(not item["optional"] for item in model["reported_address"]["fields"])
    assert [(item["name"], item["tag"]) for item in model["address_info_report"]["alternatives"]] == [("struct-info", 1), ("unstruct-info", 2)]
    for key in ("reported_struct_fields",):
        fields = model[key]
        assert len(fields) == 9
        assert [item["tag"] for item in fields] == list(range(9))
        assert all(item["optional"] for item in fields)
        assert fields[0]["size_max"] == 32
        assert all(item["size_max"] == 128 for item in fields[1:])
    requested = model["requested_address"]["fields"]
    assert len(requested) == 9 and [item["tag"] for item in requested] == list(range(9))
    assert all(item["optional"] for item in requested)
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
    print("PASS: Order 573 appendix 9 Addresses.asn; 34 rules, 14 evidence nodes, 5 enum values, 18 structured field definitions, 64 cases")


if __name__ == "__main__":
    main()
