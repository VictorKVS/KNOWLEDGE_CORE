#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-73-2010/data-network-sorm-requirements-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-73-2010/data-network-sorm-requirements-regression-v1.json")


def evaluate(c):
    q = c["query"]
    if q == "version": return "CURRENT_1196_SCOPE_TEXT" if date.fromisoformat(c["as_of"]) >= date(2026, 3, 15) else "PRE_1196_SCOPE_TEXT"
    if q == "scope": return "IN_SCOPE" if c["service"] in {"TELEMATIC", "DATA"} else "OUT_OF_SCOPE"
    if q == "part1": return "PASS" if c["order6_applied"] else "BLOCK_MISSING_PART_I"
    if q == "placement": return "PASS" if c["in_plan"] and c["at_operator_node"] else "BLOCK_PLACEMENT"
    if q == "access": return "PASS" if c["all_network_information"] and c["controlled_only"] and c["control_point"] else "BLOCK_ACCESS_ROUTE"
    if q == "dynamic_protocol": return "SUPPORTED_BY_APPENDIX2" if c["protocol"] in {"RADIUS", "TACACS_PLUS", "DIAMETER"} else "NOT_LISTED_BY_ORDER73"
    if q == "ip_sequence": return "PASS" if c["pre_nat"] and c["before_first_packet"] and c["termination"] else "BLOCK_IP_SEQUENCE"
    if q == "content_sequence": return "PASS" if c["original_form"] and c["original_sequence"] else "BLOCK_FORM_OR_SEQUENCE"
    if q == "location":
        if not c["technology_capable"]: return "EXCEPTION_APPLIES"
        return "PASS" if c["provided"] else "BLOCK_LOCATION_MISSING"
    if q == "interfaces": return "PASS" if (c["families"], c["entries"]) == (5, 25) else "BLOCK_INTERFACE_CATALOG"
    if q == "family_count":
        expected = {"ETHERNET_CSMA_CD":11, "SDH_OPTICAL":4, "PDH_OPTICAL":2, "PDH_SDH_ELECTRICAL":4, "DATA_EQUIPMENT_ELECTRICAL":4}
        return "PASS" if c["count"] == expected[c["family"]] else "BLOCK_INTERFACE_CATALOG"
    if q == "radius":
        if c["event"] == "ALLOCATION": ok = (c["code"], c["attributes"], c["type40"]) == (4, 5, 1)
        else: ok = (c["code"], c["attributes"], c["type40"]) == (5, 6, 2)
        return "PASS" if ok else "BLOCK_RADIUS_SCHEMA"
    if q == "tacacs":
        if c["event"] == "ALLOCATION": ok = c["type"] == 3 and c["flag"] in {8, 2} and c["fields"] == 5
        else: ok = (c["type"], c["flag"], c["fields"]) == (3, 4, 6)
        return "PASS" if ok else "BLOCK_TACACS_SCHEMA"
    if q == "diameter":
        expected = 2 if c["event"] == "ALLOCATION" else 4
        ok = (c["command"], c["attributes"], c["value480"]) == (271, 6, expected)
        return "PASS" if ok else "BLOCK_DIAMETER_SCHEMA"
    if q == "asterisk": return "PASS_VARIABLE_VALUE" if c["field_present"] else "BLOCK_MISSING_FIELD"
    if q == "unstated_period": return "NOT_STATED_DO_NOT_INVENT"
    if q == "closed_methods": return "BLOCK_OUT_OF_SCOPE"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 48
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 18
    assert len(model["temporal_model"]) == 2
    assert model["interface_catalog"]["family_count"] == 5
    assert model["interface_catalog"]["interface_count"] == 25
    assert sum(x["count"] for x in model["interface_catalog"]["families"]) == 25
    assert model["dynamic_ip_message_schemas"]["protocol_count"] == 3
    assert model["source"]["amendment"]["exact_effect_on_order73"] == "REPLACED_ONLY_FIRST_PARAGRAPH_OF_REQUIREMENTS_POINT1"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 56
    failures=[]
    for case in fixtures["cases"]:
        actual=evaluate(case)
        if actual != case["expected"]: failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 73 current data-network layer; 48 rules, 5 interface families, 25 entries, 3 protocols, 11 tables, 56 cases")


if __name__ == "__main__": main()
