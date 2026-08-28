#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-ip-telephone-numbering-records-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-dictionaries-ip-telephone-numbering-records-regression-v1.json")


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
        limits = {
            "area-code-length": (0, 6),
            "min-subscr-nr-length": (1, 15),
            "max-subscr-nr-length": (1, 15),
            "utc-min": (-12, 12),
            "utc-max": (-12, 12),
            "capacity-size": (1, 10000000),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_RANGE"
    if query == "size":
        limits = {
            "ip-description": (1, 256),
            "iso-alpha-2": (2, 2),
            "iso-alpha-3": (3, 3),
            "country-code": (3, 3),
            "national-significant-number": (14, 14),
            "location": (0, 256),
            "operating-company-number": (0, 4),
        }
        minimum, maximum = limits[case["target"]]
        return "PASS" if minimum <= case["value"] <= maximum else "BLOCK_SIZE"
    if query == "syntax_claim":
        return "PENDING_PRIMARY_PDF"
    if query == "relational_claim":
        return "BLOCK_NOT_SPECIFIED"
    raise AssertionError(query)


def field(fields, name):
    return next(item for item in fields if item["name"] == name)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 48
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 16
    assert len(model["report_wrappers"]) == 2
    assert all(item["count_constraint"] == "NOT_SPECIFIED" for item in model["report_wrappers"])
    ip_fields = model["records"]["IpNumberingPlanRecord"]["fields"]
    tel_fields = model["records"]["TelephoneNumberingPlanRecord"]["fields"]
    assert len(ip_fields) == 6 and sum(not item["optional"] for item in ip_fields) == 5
    assert len(tel_fields) == 24 and sum(not item["optional"] for item in tel_fields) == 20
    assert field_result(ip_fields, "end-time") == "PASS_OPTIONAL"
    assert [(item["name"], item["tag"]) for item in tel_fields if item.get("optional")] == [
        ("range-deactivation", 0), ("range-status", 1), ("description", 2), ("operating-company-number", 3)
    ]
    assert field(tel_fields, "country-code")["type"] == "UTF8String"
    assert field(tel_fields, "country-code")["size_exact"] == 3
    assert field(tel_fields, "national-significant-number")["size_exact"] == 14
    assert field(tel_fields, "area-code-length")["minimum"] == 0 and field(tel_fields, "area-code-length")["maximum"] == 6
    for name in ("min-subscr-nr-length", "max-subscr-nr-length"):
        assert field(tel_fields, name)["minimum"] == 1 and field(tel_fields, name)["maximum"] == 15
    for name in ("utc-min", "utc-max"):
        assert field(tel_fields, name)["minimum"] == -12 and field(tel_fields, name)["maximum"] == 12
    assert field(tel_fields, "capacity-size")["minimum"] == 1
    assert field(tel_fields, "capacity-size")["maximum"] == 10000000
    assert field(tel_fields, "location")["size_min"] == field(tel_fields, "registrar")["size_min"] == 0
    assert field(tel_fields, "mobile-country-code")["type"] == "NumericString"
    assert field(tel_fields, "mobile-country-code")["size_exact"] == 3
    assert field(tel_fields, "mobile-network-code")["size_exact"] == 3
    assert field(tel_fields, "range-deactivation")["syntax_status"].startswith("PENDING_PRIMARY_PDF")
    assert field(tel_fields, "range-status")["constraint_status"].startswith("PENDING_PRIMARY_PDF")
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
    print("PASS: Order 573 Dictionaries IP/telephone numbering; 48 rules, 16 evidence nodes, 30 fields, 64 cases")


if __name__ == "__main__":
    main()
