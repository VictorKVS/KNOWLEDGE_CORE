#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-doc-ipdata-special-records-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-doc-ipdata-special-records-regression-v1.json")


def field_result(fields, name):
    item = next((field for field in fields if field["name"] == name), None)
    if item is None:
        return "BLOCK_UNKNOWN_FIELD"
    return "PASS_OPTIONAL" if item.get("optional", False) else "PASS_REQUIRED"


def evaluate(case, model):
    when = date.fromisoformat(case["date"])
    if when < date(2024, 3, 1):
        return "HISTORICAL_PRE_REPLACEMENT"
    query = case["query"]
    if query == "temporal":
        return "PASS_CURRENT_RECORD_VERSION" if when < date(2030, 3, 1) else "EXPIRED_ROUTE"
    if query == "report_wrapper":
        names = {item["name"] for item in model["report_wrappers"]}
        return "PASS" if case["name"] in names else "BLOCK_UNKNOWN_WRAPPER"
    if query == "record_field":
        return field_result(model["records"][case["record"]]["fields"], case["name"])
    if query == "range":
        limits = {"doc-type-id": (0, 65535), "point-id": (0, 1000)}
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_RANGE"
    if query == "size":
        limits = {
            "doc-description": (1, 256),
            "ipdata-description": (1, 256),
            "directory-number": (1, 32),
            "special-description": (1, 256),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_SIZE"
    if query == "sequence_count":
        if case["count"] < 0:
            return "BLOCK_INVALID_COUNT"
        return "PASS_NO_COUNT_CONSTRAINT_NO_BUSINESS_INFERENCE" if case["count"] == 0 else "PASS_NO_COUNT_CONSTRAINT"
    if query == "type_claim":
        if case["claim"] in {"DIRECTORY_NUMBER_UTF8STRING", "SPECIAL_NETWORK_ADDRESS_OPTIONAL_IPADDRESS"}:
            return "PASS"
        return "BLOCK_CONTRADICTS_SOURCE"
    if query == "business_claim":
        if case["claim"] == "SPECIAL_NETWORK_ADDRESS_REQUIRED":
            return "BLOCK_CONTRADICTS_SOURCE"
        return "BLOCK_NOT_SPECIFIED"
    if query == "source_claim":
        return "PENDING_PRIMARY_BYTES" if case["claim"] == "PRIMARY_IMMUTABLE_BYTES_VERIFIED" else "BLOCK_UNVERIFIED"
    raise AssertionError(query)


def field(fields, name):
    return next(item for item in fields if item["name"] == name)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 40
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 14
    assert len(model["report_wrappers"]) == 3
    assert all(item["count_constraint"] == "NOT_SPECIFIED" for item in model["report_wrappers"])
    records = model["records"]
    assert {name: len(value["fields"]) for name, value in records.items()} == {
        "DocTypesRecord": 5, "IpDataPointRecord": 5, "SpecialNumberRecord": 6
    }
    assert {name: sum(not item["optional"] for item in value["fields"]) for name, value in records.items()} == {
        "DocTypesRecord": 4, "IpDataPointRecord": 4, "SpecialNumberRecord": 4
    }
    assert field(records["DocTypesRecord"]["fields"], "doc-type-id")["minimum"] == 0
    assert field(records["DocTypesRecord"]["fields"], "doc-type-id")["maximum"] == 65535
    assert field(records["IpDataPointRecord"]["fields"], "point-id")["minimum"] == 0
    assert field(records["IpDataPointRecord"]["fields"], "point-id")["maximum"] == 1000
    for record in records.values():
        assert field_result(record["fields"], "end-time") == "PASS_OPTIONAL"
    directory = field(records["SpecialNumberRecord"]["fields"], "directory-number")
    assert directory["type"] == "UTF8String" and directory["size_min"] == 1 and directory["size_max"] == 32
    network = field(records["SpecialNumberRecord"]["fields"], "network-address")
    assert network["type"] == "IPAddress" and network["optional"] is True
    assert "special-number-type" not in {item["name"] for item in records["SpecialNumberRecord"]["fields"]}
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
    print("PASS: Order 573 Dictionaries doc/IP-data/special; 40 rules, 14 evidence nodes, 16 fields, 64 cases")


if __name__ == "__main__":
    main()
