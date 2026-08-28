#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-mobile-identity-signal-point-records-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-mobile-identity-signal-point-records-regression-v1.json")


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
        if case["name"] in names:
            return "PASS"
        return "BLOCK_NORMALIZED_ALIAS"
    if query == "record_field":
        return field_result(model["records"][case["record"]]["fields"], case["name"])
    if query == "size":
        limits = {
            "mcc": (3, 3), "mnc": (3, 3), "area-code": (3, 10),
            "capacity-from": (0, 7), "capacity-to": (0, 7),
            "mobile-description": (2, 255), "region": (1, 128),
            "range-status": (2, 128), "ss7-point-code": (1, 32),
            "signal-switch-id": (1, 128), "signal-description": (1, 256),
        }
        minimum, maximum = limits[case["target"]]
        if not minimum <= case["value"] <= maximum:
            return "BLOCK_SIZE"
        if minimum == 0 and case["value"] == 0:
            return "PASS_SYNTAX_ONLY_NO_BUSINESS_INFERENCE"
        return "PASS"
    if query == "range":
        return "PASS" if 1 <= case["value"] <= 10000000 else "BLOCK_RANGE"
    if query == "literal_name":
        return "PASS" if case["name"] == "MobileSubscriberIdenityPlanRecord" else "BLOCK_NORMALIZED_ALIAS"
    if query == "business_claim":
        return "BLOCK_NOT_SPECIFIED"
    if query == "syntax_claim":
        return "PENDING_PRIMARY_PDF" if case["claim"] == "ALL_RENDERED_TOKENS_COMPILE" else "BLOCK_UNVERIFIED"
    if query == "sequence_count":
        if case["count"] < 0:
            return "BLOCK_INVALID_COUNT"
        return "PASS_NO_COUNT_CONSTRAINT_NO_BUSINESS_INFERENCE" if case["count"] == 0 else "PASS_NO_COUNT_CONSTRAINT"
    raise AssertionError(query)


def field(fields, name):
    return next(item for item in fields if item["name"] == name)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 48
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 16
    assert len(model["report_wrappers"]) == 2
    wrappers = {item["name"]: item for item in model["report_wrappers"]}
    assert set(wrappers) == {"mobileSubscriberIdenityPlanRecords", "signalPointCodes"}
    assert wrappers["mobileSubscriberIdenityPlanRecords"]["item_type"] == "MobileSubscriberIdenityPlanRecord"
    assert wrappers["signalPointCodes"]["item_type"] == "SignalPointCodesRecord"
    assert all(item["count_constraint"] == "NOT_SPECIFIED" for item in wrappers.values())
    records = model["records"]
    mobile = records["MobileSubscriberIdenityPlanRecord"]["fields"]
    signal = records["SignalPointCodesRecord"]["fields"]
    assert len(mobile) == 13 and sum(not item["optional"] for item in mobile) == 11
    assert len(signal) == 5 and sum(not item["optional"] for item in signal) == 4
    assert [(item["name"], item.get("tag")) for item in mobile if item["optional"]] == [
        ("range-deactivation", 0), ("range-status", 1)
    ]
    assert field(mobile, "mcc")["size_exact"] == field(mobile, "mnc")["size_exact"] == 3
    assert (field(mobile, "area-code")["size_min"], field(mobile, "area-code")["size_max"]) == (3, 10)
    assert (field(mobile, "capacity-from")["size_min"], field(mobile, "capacity-from")["size_max"]) == (0, 7)
    assert (field(mobile, "capacity-to")["size_min"], field(mobile, "capacity-to")["size_max"]) == (0, 7)
    assert (field(mobile, "capacity-size")["minimum"], field(mobile, "capacity-size")["maximum"]) == (1, 10000000)
    assert field(mobile, "range-activation")["rendered_token"] == "DateAnd Time"
    assert field(mobile, "range-deactivation")["rendered_token"] == "DateAndTimeOPTIONAL"
    assert field_result(signal, "telco-id") == "BLOCK_UNKNOWN_FIELD"
    assert field(signal, "switch-id")["rendered_token"] == "switch-idUTF8String"
    assert field(signal, "begin-time")["rendered_token"] == "begin-timeDateAndTime"
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
    print("PASS: Order 573 Dictionaries mobile identity/signal point; 48 rules, 16 evidence nodes, 18 fields, 64 cases")


if __name__ == "__main__":
    main()
