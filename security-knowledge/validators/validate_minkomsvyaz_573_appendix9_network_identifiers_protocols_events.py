#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-network-identifiers-protocols-events-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-network-identifiers-protocols-events-regression-v1.json")

def field(items, name):
    return next((item for item in items if item["name"] == name), None)

def enum_map(type_model):
    values = type_model["values"]
    if isinstance(values, dict):
        return values
    return {item["name"]: item["value"] for item in values}

def evaluate(case, model):
    query = case["query"]
    types = model["types"]
    if query == "temporal":
        observed = date.fromisoformat(case["date"])
        if observed < date(2024, 3, 1):
            return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_NETWORK_IDENTIFIERS_VERSION" if observed < date(2030, 3, 1) else "EXPIRED_ROUTE"
    if query == "field":
        item = field(types["DataVoipNumber"]["fields"], case["name"])
        return "BLOCK_UNKNOWN_FIELD" if item is None else ("PASS_OPTIONAL" if item["optional"] else "PASS_REQUIRED")
    if query == "boundary":
        item = field(types["DataVoipNumber"]["fields"], case["target"])
        return "PASS" if item["size_min"] <= case["value"] <= item["size_max"] else "BLOCK_SIZE"
    if query == "semantic":
        return {
            "empty-data-voip": "PASS_ASN1_SYNTAX_ONLY_BUSINESS_MEANING_UNSPECIFIED",
            "e164-format": "NOT_SPECIFIED",
            "original-format": "NOT_SPECIFIED",
            "cross-field-relation": "NOT_SPECIFIED",
        }[case["target"]]
    if query == "syntax":
        return "PENDING_PRIMARY_PDF"
    if query == "enum":
        values = enum_map(types[case["type"]])
        return "PASS" if values.get(case["name"]) == case["value"] else "BLOCK_UNKNOWN_ENUM"
    if query == "enum-count":
        return "PASS" if len(enum_map(types[case["type"]])) == case["value"] else "BLOCK_COUNT_MISMATCH"
    raise AssertionError(query)

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    types = model["types"]
    rules = model["atomic_rules"]
    evidence = model["evidence_model"]
    assert len(rules) == len({item["id"] for item in rules}) == 64
    assert [item["id"] for item in rules] == [f"MK573NIP-R{i:03d}" for i in range(1, 65)]
    assert len(evidence) == len({item["id"] for item in evidence}) == 18
    proved = [rule_id for node in evidence for rule_id in node["proves"]]
    assert proved == [item["id"] for item in rules]
    completion = model["module_completion"]
    assert completion["exports_total"] == completion["deep_exports_complete"] == 13
    assert completion["core_exports_previously_atomized"] == 8
    assert len(completion["exports_atomized_here"]) == 5 and completion["remaining_exports"] == 0
    data_voip = types["DataVoipNumber"]
    assert len(data_voip["fields"]) == 3 and all(item["optional"] for item in data_voip["fields"])
    assert [(item["name"], item["tag"], item["size_min"], item["size_max"]) for item in data_voip["fields"]] == [
        ("original-number", None, 1, 2048),
        ("translated-number", 0, 1, 32),
        ("e164-number", 1, 1, 15),
    ]
    assert enum_map(types["VoipProtocol"]) == {"sip": 0, "h323": 1, "iax": 2, "skype": 100}
    im_values = types["IMProtocol"]["values"]
    assert len(im_values) == types["IMProtocol"]["value_count"] == 40
    assert len({item["name"] for item in im_values}) == len({item["value"] for item in im_values}) == 40
    assert [item["value"] for item in im_values[:11]] == list(range(11))
    assert [item["value"] for item in im_values[11:20]] == [98, 99, 100, 101, 102, 103, 104, 105, 106]
    assert [item["value"] for item in im_values[20:]] == list(range(151, 171))
    assert [(item["name"], item["value"]) for item in im_values[24:]] == [(f"rezerv {i}", i + 150) for i in range(5, 21)]
    assert all(item["syntax_status"] == "PENDING_PRIMARY_PDF_SPACE_IN_IDENTIFIER" for item in im_values[24:])
    assert enum_map(types["HttpMethod"]) == {"get": 0, "post": 1, "put": 2, "delete": 3}
    assert enum_map(types["EntranceEventType"]) == {
        "registration": 0, "logon": 1, "logon-failure": 2, "logoff": 3,
        "add-service": 4, "update-service": 5, "del-service": 6,
        "add-domain": 7, "del-domain": 8, "create-support-ticket": 9,
        "update-profile": 10, "other": 11,
    }
    assert len(fixtures["cases"]) == len({item["id"] for item in fixtures["cases"]}) == 64
    failures = [(case["id"], case["expected"], evaluate(case, model)) for case in fixtures["cases"] if evaluate(case, model) != case["expected"]]
    if failures:
        print(*failures, sep="\n")
        raise SystemExit(1)
    boundary = model["verification_boundary"]
    assert not boundary["critical_gap_created"] and not boundary["high_gap_created"]
    print("PASS: Order 573 NetworkIdentifiers remaining exports; 64 rules, 18 evidence nodes, 5 deep exports, 40 IM values, 64 cases")

if __name__ == "__main__":
    main()
