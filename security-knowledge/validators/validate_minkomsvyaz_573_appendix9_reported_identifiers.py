#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reported-identifiers-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reported-identifiers-regression-v1.json")

def named(items, name):
    return next((item for item in items if item["name"] == name), None)

def evaluate(case, model):
    query = case["query"]
    if query == "temporal":
        observed = date.fromisoformat(case["date"])
        if observed < date(2024, 3, 1):
            return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTED_IDENTIFIERS_VERSION" if observed < date(2030, 3, 1) else "EXPIRED_ROUTE"
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
    if query == "boundary-type":
        item = model["types"][case["type"]]
        return "PASS" if item["size_min"] <= case["value"] <= item["size_max"] else "BLOCK_SIZE"
    if query == "field":
        item = named(model["types"][case["type"]]["fields"], case["name"])
        if item is None:
            return "BLOCK_UNKNOWN_FIELD"
        if item.get("tag") != case["tag"]:
            return "BLOCK_TAG_MISMATCH"
        return "PASS_OPTIONAL" if item["optional"] else "PASS_REQUIRED"
    if query == "boundary-field":
        item = named(model["types"][case["type"]]["fields"], case["name"])
        return "PASS" if item["size_min"] <= case["value"] <= item["size_max"] else "BLOCK_SIZE"
    if query == "syntax":
        return "PENDING_PRIMARY_PDF"
    if query == "semantic":
        if case["target"] in {"empty-data-network", "empty-voip"}:
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
    assert [item["id"] for item in rules] == [f"MK573RI-R{i:03d}" for i in range(1, 65)]
    assert len(evidence) == len({item["id"] for item in evidence}) == 18
    assert [rule for node in evidence for rule in node["proves"]] == [item["id"] for item in rules]
    assert model["module"]["exports"] == ["ReportedIdentifier"]
    assert len(model["module"]["imports"]["Classification"]) == 7
    assert model["module"]["imports"]["NetworkIdentifiers"] == ["IPAddress", "DataNetworkEquipment", "IPMask"]
    assert len(model["variants"]) == 6
    assert [(item["name"], item["oid"], item["data_type"]) for item in model["variants"]] == [
        ("reportedPagerIdentifier", "sorm-report-identifier-pager", "ReportedPagerIdentifier"),
        ("reportedPstnIdentifier", "sorm-report-identifier-pstn", "ReportedPstnIdentifier"),
        ("reportedGsmIdentifier", "sorm-report-identifier-gsm", "ReportedGsmIdentifier"),
        ("reportedCdmaIdentifier", "sorm-report-identifier-cdma", "ReportedCdmaIdentifier"),
        ("reportedDataNetworkIdentifier", "sorm-report-identifier-data-network", "ReportedDataNetworkIdentifier"),
        ("reportedVoipIdentifier", "sorm-report-identifier-voip", "ReportedVoipIdentifier"),
    ]
    assert (types["ReportedPagerIdentifier"]["size_min"], types["ReportedPagerIdentifier"]["size_max"]) == (2, 18)
    pstn = types["ReportedPstnIdentifier"]["fields"]
    assert [(item["name"], item["type"], item["optional"], item["tag"], item["size_min"], item["size_max"]) for item in pstn] == [
        ("directory-number", "UTF8String", False, None, 1, 32),
        ("intemal-number", "NumericString", True, None, 1, 32),
    ]
    gsm = types["ReportedGsmIdentifier"]["fields"]
    assert [(item["name"], item["tag"], item["optional"]) for item in gsm] == [("directory-number", None, False), ("imsi", None, False), ("imei", 0, True), ("icc", 1, True)]
    cdma = types["ReportedCdmaIdentifier"]["fields"]
    assert [(item["name"], item["tag"], item["optional"]) for item in cdma] == [("directory-number", None, False), ("imsi", None, False), ("esn", 0, True), ("min", 1, True), ("icc", 2, True)]
    data_fields = types["ReportedDataNetworkIdentifier"]["fields"]
    assert len(data_fields) == 9 and all(item["optional"] for item in data_fields)
    assert [item["tag"] for item in data_fields] == list(range(9))
    voip_fields = types["ReportedVoipIdentifier"]["fields"]
    assert len(voip_fields) == 3 and all(item["optional"] for item in voip_fields)
    assert [item["tag"] for item in voip_fields] == [0, 1, 2]
    assert len(fixtures["cases"]) == len({item["id"] for item in fixtures["cases"]}) == 64
    failures = [(case["id"], case["expected"], evaluate(case, model)) for case in fixtures["cases"] if evaluate(case, model) != case["expected"]]
    if failures:
        print(*failures, sep="\n")
        raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"] and not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportedIdentifiers; 64 rules, 18 evidence nodes, 6 variants, 23 sequence fields plus pager scalar, 64 cases")

if __name__ == "__main__":
    main()
