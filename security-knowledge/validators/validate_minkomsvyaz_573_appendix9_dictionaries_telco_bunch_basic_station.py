#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-telco-bunch-basic-station-records-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-telco-bunch-basic-station-records-regression-v1.json")


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
    if query == "record_field":
        return field_result(model["records"][case["record"]]["fields"], case["name"])
    if query == "bunch_type":
        values = {item["value"]: item["name"] for item in model["records"]["BunchRecord"]["bunch_type"]["values"]}
        return f"PASS_{values[case['value']].upper()}" if case["value"] in values else "BLOCK_UNASSIGNED_VALUE"
    if query == "identifier_choice":
        values = {item["name"]: item["tag"] for item in model["basic_station_identifiers"]["alternatives"]}
        return f"PASS_TAG_{values[case['name']]}" if case["name"] in values else "BLOCK_UNKNOWN_OR_MULTIPLE_CHOICE"
    if query == "antenna_choice":
        values = {item["name"]: item["tag"] for item in model["basic_station_antenna"]["alternatives"]}
        return f"PASS_TAG_{values[case['name']]}" if case["name"] in values else "BLOCK_UNKNOWN_OR_MULTIPLE_CHOICE"
    if query == "range":
        limits = {
            "telephone-lac": (0, 65535),
            "telephone-cell": (0, 100000000000),
            "gsm-azimuth": (-1, 359),
            "gsm-power": (0, 25000),
            "gsm-frequency": (0, 100000000000),
            "broadband-frequency-start": (0, 10000000000),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_RANGE"
    if query == "size":
        limits = {
            "telephone-cell-sign": (1, 18),
            "wireless-cell": (1, 64),
            "wireless-mac": (6, 6),
            "gsm-controller-num": (1, 128),
            "gsm-channel": (1, 32),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_SIZE"
    if query == "sequence_count":
        assert case["target"] == "IPList"
        return "PASS_NO_COUNT_CONSTRAINT" if case["count"] >= 0 else "BLOCK_INVALID_COUNT"
    if query == "enum":
        group = model["enumerations"][case["target"]]
        values = group["values"] if isinstance(group, dict) else group
        mapping = {item["name"]: item["value"] for item in values}
        return "PASS" if mapping.get(case["name"]) == case["value"] else "BLOCK_ENUM"
    if query == "syntax_claim":
        return "BLOCK_PENDING_PRIMARY_PDF"
    raise AssertionError(query)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 48
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 16
    assert len(model["report_wrappers"]) == 3
    assert all(item["count_constraint"] == "NOT_SPECIFIED" for item in model["report_wrappers"])
    assert {key: len(value["fields"]) for key, value in model["records"].items()} == {
        "TelcosRecord": 6, "BunchRecord": 7, "BasicStationSectorRecord": 9
    }
    assert field_result(model["records"]["TelcosRecord"]["fields"], "end-time") == "PASS_OPTIONAL"
    assert field_result(model["records"]["BunchRecord"]["fields"], "end-time") == "PASS_OPTIONAL"
    assert field_result(model["records"]["BasicStationSectorRecord"]["fields"], "end-time") == "PASS_REQUIRED"
    assert [(item["name"], item["value"]) for item in model["records"]["BunchRecord"]["bunch_type"]["values"]] == [
        ("inbound", 0), ("outbound", 1), ("bidirectional", 3)
    ]
    assert len(model["basic_station_identifiers"]["alternatives"]) == 2
    assert len(model["telephone_identifiers"]["fields"]) == 3
    assert len(model["wireless_identifiers"]["fields"]) == 3
    assert model["ip_list"]["count_constraint"] == "NOT_SPECIFIED"
    assert len(model["basic_station_antenna"]["alternatives"]) == 3
    assert len(model["gsm_antenna"]["required_fields"]) == 3
    assert len(model["gsm_antenna"]["optional_fields"]) == 14
    assert [item["tag"] for item in model["gsm_antenna"]["optional_fields"]] == list(range(14))
    assert model["enumerations"]["BsSetting"]["declaration_status"].startswith("PENDING_PRIMARY_PDF")
    assert model["antenna_aliases"] == {
        "CdmaAntenna": "BroadbandWirelessParameters", "WirelessAntenna": "BroadbandWirelessParameters"
    }
    assert len(model["broadband_wireless_parameters"]["required_fields"]) == 3
    assert len(model["broadband_wireless_parameters"]["optional_fields"]) == 7
    assert [item["tag"] for item in model["broadband_wireless_parameters"]["optional_fields"]] == list(range(7))
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
    print("PASS: Order 573 Dictionaries deep telco/bunch/basic-station records; 48 rules, 16 evidence nodes, 64 cases")


if __name__ == "__main__":
    main()
