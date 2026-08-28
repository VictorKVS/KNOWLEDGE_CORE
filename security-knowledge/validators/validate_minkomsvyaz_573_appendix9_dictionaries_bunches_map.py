#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-bunches-map-records-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-bunches-map-records-regression-v1.json")


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
    if query == "type_claim":
        valid = {"A_BUNCH_BUNCH_MAP_POINT", "B_BUNCH_BUNCH_MAP_POINT", "POINT_TELCO_ID_TELCO_ID", "POINT_SWITCH_ID_UTF8STRING"}
        return "PASS" if case["claim"] in valid else "BLOCK_CONTRADICTS_SOURCE"
    if query == "size":
        return "PASS" if 1 <= case["value"] <= 128 else "BLOCK_SIZE"
    if query == "range":
        return "PASS" if 0 <= case["value"] <= 65535 else "BLOCK_RANGE"
    if query == "sequence_count":
        if case["count"] < 0:
            return "BLOCK_INVALID_COUNT"
        return "PASS_NO_COUNT_CONSTRAINT_NO_BUSINESS_INFERENCE" if case["count"] == 0 else "PASS_NO_COUNT_CONSTRAINT"
    if query == "pair_claim":
        return "BLOCK_NOT_SPECIFIED"
    if query == "business_claim":
        if case["claim"] in {"END_TIME_REQUIRED", "A_BUNCH_OPTIONAL", "B_BUNCH_OPTIONAL"}:
            return "BLOCK_CONTRADICTS_SOURCE"
        return "BLOCK_NOT_SPECIFIED"
    if query == "time_claim":
        if case["claim"] == "OPEN_ENDED_RELATIONSHIP_ALLOWED_BY_OPTIONAL_FIELD":
            return "PASS_SYNTAX_ONLY_NO_BUSINESS_INFERENCE"
        return "BLOCK_NOT_SPECIFIED"
    if query == "source_claim":
        return "PENDING_PRIMARY_BYTES" if case["claim"] == "PRIMARY_IMMUTABLE_BYTES_VERIFIED" else "PASS"
    if query == "dependency_claim":
        return "PASS" if case["claim"] == "TELCO_ID_DEEP_MODEL_LINKED" else "PENDING_DEPENDENCY"
    if query == "wrapper_claim":
        valid = {"OID_SORM_REPORT_DICTIONARY_BUNCHES_MAP", "DATA_SEQUENCE_OF_BUNCHES_MAP_RECORD"}
        return "PASS" if case["claim"] in valid else "BLOCK_CONTRADICTS_SOURCE"
    if query == "field_count":
        return "PASS" if len(model["records"][case["record"]]["fields"]) == case["value"] else "BLOCK_COUNT"
    if query == "syntax_claim":
        return "BLOCK_UNVERIFIED"
    if query == "literal_name":
        return "PASS" if case["name"] == "BunchesMapRecord" else "BLOCK_NORMALIZED_ALIAS"
    raise AssertionError(query)


def field(fields, name):
    return next(item for item in fields if item["name"] == name)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 40
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 14
    assert len(model["report_wrappers"]) == 1
    wrapper = model["report_wrappers"][0]
    assert wrapper == {
        "name": "bunchesMapRecords",
        "oid": "sorm-report-dictionary-bunches-map",
        "item_type": "BunchesMapRecord",
        "count_constraint": "NOT_SPECIFIED",
    }
    records = model["records"]
    assert {name: len(value["fields"]) for name, value in records.items()} == {
        "BunchesMapRecord": 4, "BunchMapPoint": 3
    }
    assert {name: sum(not item["optional"] for item in value["fields"]) for name, value in records.items()} == {
        "BunchesMapRecord": 3, "BunchMapPoint": 3
    }
    mapping = records["BunchesMapRecord"]["fields"]
    assert field(mapping, "a-bunch")["type"] == "BunchMapPoint"
    assert field(mapping, "b-bunch")["type"] == "BunchMapPoint"
    assert field_result(mapping, "end-time") == "PASS_OPTIONAL"
    point = records["BunchMapPoint"]["fields"]
    switch = field(point, "switch-id")
    assert switch["type"] == "UTF8String" and switch["size_min"] == 1 and switch["size_max"] == 128
    assert field(point, "telco-id")["type"] == "TelcoID"
    assert field(point, "bunch-id")["type"] == "Bunch"
    assert all(not item["optional"] for item in point)
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
    print("PASS: Order 573 Dictionaries bunches map; 40 rules, 14 evidence nodes, 7 fields, 64 cases")


if __name__ == "__main__":
    main()
