#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-roaming-switches-gates-records-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-roaming-switches-gates-records-regression-v1.json")


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
        limits = {"roaming-id": (0, 4294967295), "gate-id": (0, 4294967295)}
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_RANGE"
    if query == "size":
        limits = {
            "roaming-description": (1, 256),
            "switch-id": (1, 128),
            "switch-sign": (1, 18),
            "switch-description": (1, 256),
            "gate-description": (1, 256),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_SIZE"
    if query == "switch_type":
        values = {item["value"]: item["name"] for item in model["records"]["SwitchesRecord"]["switch_type"]["values"]}
        return f"PASS_{values[case['value']].upper()}" if case["value"] in values else "BLOCK_UNKNOWN_VALUE"
    if query == "gate_type":
        values = {item["value"]: item["name"] for item in model["records"]["GatesRecord"]["gate_type"]["values"]}
        return f"PASS_{values[case['value']].upper()}" if case["value"] in values else "BLOCK_UNKNOWN_VALUE"
    if query == "sequence_count":
        if case["count"] < 0:
            return "BLOCK_INVALID_COUNT"
        return "PASS_NO_COUNT_CONSTRAINT_NO_BUSINESS_INFERENCE" if case["count"] == 0 else "PASS_NO_COUNT_CONSTRAINT"
    if query == "business_claim":
        return "BLOCK_NOT_SPECIFIED"
    raise AssertionError(query)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 40
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 14
    assert len(model["report_wrappers"]) == 3
    assert all(item["count_constraint"] == "NOT_SPECIFIED" for item in model["report_wrappers"])
    assert {key: len(value["fields"]) for key, value in model["records"].items()} == {
        "RoamingPartnerRecord": 5, "SwitchesRecord": 9, "GatesRecord": 8
    }
    for record in model["records"].values():
        assert field_result(record["fields"], "end-time") == "PASS_OPTIONAL"
    assert sum(not item["optional"] for item in model["records"]["RoamingPartnerRecord"]["fields"]) == 4
    assert sum(not item["optional"] for item in model["records"]["SwitchesRecord"]["fields"]) == 7
    assert sum(not item["optional"] for item in model["records"]["GatesRecord"]["fields"]) == 7
    assert [(item["name"], item["value"]) for item in model["records"]["SwitchesRecord"]["switch_type"]["values"]] == [
        ("internal", 0), ("border", 1)
    ]
    assert [(item["name"], item["value"]) for item in model["records"]["GatesRecord"]["gate_type"]["values"]] == [
        ("sgsn", 0), ("ggsn", 1), ("smsc", 2), ("gmsc", 3), ("hss", 4),
        ("pstn", 5), ("voip-gw", 6), ("aaa", 7), ("nat", 8)
    ]
    assert model["sequence_semantics"]["gate_ip_list"]["count_constraint"] == "NOT_SPECIFIED"
    assert model["sequence_semantics"]["gate_ip_list"]["empty_sequence_business_status"].startswith("NOT_SPECIFIED")
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
    print("PASS: Order 573 Dictionaries roaming/switches/gates; 40 rules, 14 evidence nodes, 22 fields, 11 enum values, 64 cases")


if __name__ == "__main__":
    main()
