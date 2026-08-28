#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-call-service-pay-termination-records-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-call-service-pay-termination-records-regression-v1.json")


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
        wrapper = next((item for item in model["report_wrappers"] if item["name"] == case["name"]), None)
        if wrapper is None:
            return "BLOCK_UNKNOWN_WRAPPER"
        if wrapper.get("oid_delimiter_status") == "PENDING_PRIMARY_PDF_CLOSING_DELIMITER":
            return "PASS_WITH_OID_DELIMITER_PENDING"
        return "PASS"
    if query == "record_field":
        return field_result(model["records"][case["record"]]["fields"], case["name"])
    if query == "range":
        limits = {
            "call-type-id": (0, 4294967295),
            "service-id": (0, 4294967295),
            "pay-type-id": (0, 4294967295),
            "termination-cause-id": (0, 16384),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_RANGE"
    if query == "size":
        limits = {
            "calls-description": (1, 256),
            "supplement-description": (1, 256),
            "pay-description": (1, 256),
            "termination-description": (1, 256),
            "supplement-mnemonic": (1, 64),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_SIZE"
    if query == "sequence_count":
        if case["count"] < 0:
            return "BLOCK_INVALID_COUNT"
        return "PASS_NO_COUNT_CONSTRAINT_NO_BUSINESS_INFERENCE" if case["count"] == 0 else "PASS_NO_COUNT_CONSTRAINT"
    if query == "record_literal":
        return "PASS_LITERAL_SOURCE_NAME" if case["name"] == "CallsTypesRecord" else "BLOCK_NORMALIZED_ALIAS"
    if query == "syntax_claim":
        if case["claim"] == "TERMINATION_CAUSES_OID_CLOSING_DELIMITER":
            return "PENDING_PRIMARY_PDF"
        return "BLOCK_UNVERIFIED"
    raise AssertionError(query)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 40
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 14
    assert len(model["report_wrappers"]) == 4
    assert all(item["count_constraint"] == "NOT_SPECIFIED" for item in model["report_wrappers"])
    assert {key: len(value["fields"]) for key, value in model["records"].items()} == {
        "CallsTypesRecord": 5,
        "SupplementServicesRecord": 6,
        "PayTypesRecord": 5,
        "TerminationCausesRecord": 6,
    }
    assert {key: sum(not field["optional"] for field in value["fields"]) for key, value in model["records"].items()} == {
        "CallsTypesRecord": 4,
        "SupplementServicesRecord": 4,
        "PayTypesRecord": 4,
        "TerminationCausesRecord": 5,
    }
    for record in model["records"].values():
        assert field_result(record["fields"], "end-time") == "PASS_OPTIONAL"
    mnemonic = next(item for item in model["records"]["SupplementServicesRecord"]["fields"] if item["name"] == "mnemonic")
    assert mnemonic == {"name": "mnemonic", "type": "UTF8String", "size_min": 1, "size_max": 64, "optional": True}
    termination = model["records"]["TerminationCausesRecord"]["fields"]
    cause = next(item for item in termination if item["name"] == "termination-cause-id")
    assert cause["minimum"] == 0 and cause["maximum"] == 16384
    assert field_result(termination, "network-type") == "PASS_REQUIRED"
    assert "CallsTypesRecord" in model["records"] and "CallTypesRecord" not in model["records"]
    termination_wrapper = next(item for item in model["report_wrappers"] if item["name"] == "terminationCausesRecords")
    assert termination_wrapper["oid_delimiter_status"] == "PENDING_PRIMARY_PDF_CLOSING_DELIMITER"
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
    print("PASS: Order 573 Dictionaries calls/services/pay/termination; 40 rules, 14 evidence nodes, 22 fields, 64 cases")


if __name__ == "__main__":
    main()
