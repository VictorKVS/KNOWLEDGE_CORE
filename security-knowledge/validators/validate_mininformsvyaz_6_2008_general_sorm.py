#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/mininformsvyaz-6-2008/general-sorm-requirements-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/mininformsvyaz-6-2008/general-sorm-requirements-regression-v1.json")


def evaluate(c):
    q = c["query"]
    if q == "scope":
        return "IN_SCOPE" if c["network"] in {"PUBLIC", "DEDICATED"} and c["licence_requires_sorm"] else "OUT_OF_SCOPE"
    if q == "point2": return "ROUTE_TO_POINT4" if c["service"] == "CHANNEL_PROVISION" else "APPLY_POINT2"
    if q == "identifier_transfer": return "PASS" if c["number_or_code"] and c["control_point"] else "BLOCK_IDENTIFIER_TRANSFER"
    if q == "content_transfer": return "PASS" if c["content"] and c["original_input_form"] and c["control_point"] else "BLOCK_CONTENT_TRANSFER"
    if q == "operator_encoding":
        if not c["operator_added_encoding"]: return "NO_GENERAL_DECRYPTION_RULE"
        return "PASS" if c["decoded"] else "BLOCK_OPERATOR_ENCODING"
    if q == "realtime": return "PASS" if c["during_connection_or_message"] else "BLOCK_NOT_DURING_EVENT"
    if q == "location":
        if not c["mobile_with_stable_id"]: return "NOT_TRIGGERED"
        if not c["technology_capable"]: return "EXCEPTION_APPLIES"
        return "PASS" if c["provided"] else "BLOCK_LOCATION_MISSING"
    if q == "channel_route": return "PASS" if c["requested_channel"] and c["access"] and c["transferred"] else "BLOCK_CHANNEL_ROUTE"
    if q == "request_gate": return "PASS" if c["control_point_request"] and c["controlled_information"] else "BLOCK_MISSING_REQUEST"
    if q == "connection": return "PASS" if all(c[k] for k in ("subscriber_db", "service_db", "technical_means", "technical_conditions")) else "BLOCK_CONNECTION_SET"
    if q == "subscriber_lookup": return "PASS" if c["supported"] and c["mode"] in {"NUMBER_OR_CODE", "PERSONAL_DATA_TO_NUMBER_OR_CODE"} else "BLOCK_SUBSCRIBER_LOOKUP"
    if q == "service_lookup": return "PASS" if c["supported"] and c["mode"] in {"NUMBER_OR_CODE", "OTHER_REQUEST_ATTRIBUTE"} else "BLOCK_SERVICE_LOOKUP"
    if q == "stealth": return "PASS" if c["participant_detection_prevented"] and c["personnel_unauthorized_access_prevented"] else "BLOCK_STEALTH_OR_ACCESS"
    if q == "placement": return "PASS" if c["at_operator_node"] and c["in_plan"] else "BLOCK_PLACEMENT"
    if q == "technical_conditions": return "PASS" if c["items"] == 3 else "BLOCK_INCOMPLETE_TECHNICAL_CONDITIONS"
    if q == "room_fallback":
        if c["special_requirements_exist"]: return "NOT_FALLBACK_ROUTE"
        return "PASS" if c["interacting_unit_request"] and c["room_conforming"] else "BLOCK_ROOM_ROUTE"
    if q == "room":
        payphone_ok = not c["payphones_exist"] or c["payphone_control"]
        return "PASS" if c["cross_connect"] and payphone_ok and c["access_control"] else "BLOCK_ROOM_REQUIREMENTS"
    if q == "unstated_period": return "NOT_STATED_DO_NOT_INVENT"
    if q == "legal_authority": return "PASS" if c["technical_capability"] and c["separate_lawful_basis"] else "BLOCK_MISSING_LAWFUL_BASIS"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 40
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 16
    assert len(model["temporal_model"]) == 2
    assert model["technical_conditions_required_contents"]["count"] == 3
    assert model["room_appendix"]["numbered_points"] == 4
    assert len(model["room_appendix"]["requirements"]) == 6
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 56
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]: failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: Order 6 current general SORM layer; 40 rules, 2 temporal routes, 16 evidence nodes, 3 technical-condition items, 4 appendix points, 56 cases")


if __name__ == "__main__": main()
