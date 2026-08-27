#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-645-2016/mobile-radiotelephone-sorm-equipment-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-645-2016/mobile-radiotelephone-sorm-equipment-regression-v1.json")


def evaluate(c):
    q = c["query"]
    if q == "scope":
        valid_networks = {"PUBLIC_MOBILE", "DEDICATED_MOBILE_RADIO", "DEDICATED_MOBILE_RADIOTELEPHONE"}
        return "IN_SCOPE" if c["node"] == "TERMINAL_TRANSIT_MOBILE" and c["network"] in valid_networks else "OUT_OF_SCOPE"
    if q == "decision":
        if not c["orm_decision"]: return "BLOCK_MISSING_ORM_DECISION"
        return "PASS" if c["subscriber"] else "BLOCK_NOT_CONTROL_OBJECT"
    if q == "identifiers": return "PASS" if all(c[k] for k in ("msisdn", "imsi", "imei", "phone")) else "BLOCK_IDENTIFIER_ROUTE"
    if q == "registration_states": return "PASS" if all(c[k] for k in ("home", "visitor", "unregistered")) else "BLOCK_REGISTRATION_ROUTE"
    if q == "control_modes": return "PASS" if all(c[k] for k in ("statistical", "full", "combined", "separate")) else "BLOCK_CONTROL_MODE"
    if q == "message_routes": return "PASS" if all(c[k] for k in ("successful_connection", "unsuccessful_connection", "delivered_sms", "undelivered_sms")) else "BLOCK_EVENT_ROUTE"
    if q == "event_timing":
        if c.get("treat_as_retention"): return "BLOCK_UNIT_SEMANTICS"
        return "PASS" if c["milliseconds"] <= 200 else "BLOCK_EVENT_PORT_LATENCY"
    if q == "concealment":
        if c["operator_storage_reveals"]: return "BLOCK_OPERATOR_STORAGE_DISCLOSURE"
        return "BLOCK_PARTICIPANT_DETECTION" if c["participants_detect"] else "PASS"
    if q == "appendix_topology": return "PASS" if (c["appendices"], c["body_points"]) == (13, 21) else "BLOCK_STRUCTURE"
    if q == "location": return "PASS" if all(c[k] for k in ("active", "passive", "handover_continuity")) else "BLOCK_LOCATION_ROUTE"
    if q == "interface_capacity":
        limits = {"identifiers": 2048, "phones": 1024, "separate": 112, "combined": 224}
        return "PASS" if all(c[k] <= v for k, v in limits.items()) else "BLOCK_INTERFACE_CAPACITY"
    if q == "interface_variants":
        return "PASS" if c["x25"] and c["ethernet_tcp"] and c["tcp_ports"] == 3 and c["mbps"] >= 20 else "BLOCK_INTERFACE_VARIANT"
    if q == "distributed":
        return "PASS" if all(c[k] for k in ("per_territory_interface", "territory_isolation", "per_operator_interface", "own_interface_number")) else "BLOCK_DISTRIBUTED_ISOLATION"
    if q == "lifecycle": return "ORDER645_CURRENT_ROUTE" if date.fromisoformat(c["date"]) >= date(2017, 7, 16) else "ORDER174_PREDECESSOR_ROUTE"
    if q == "byte_table":
        if c["claim_exact"] and not c["immutable_review"]: return "BLOCK_UNVERIFIED_BYTE_CLAIM"
        if c["claim_exact"]: return "PASS_IF_REVIEW_ARTIFACT_BOUND"
        return "PENDING_FAIL_CLOSED"
    if q == "current_status":
        if c["revision"] != "2016-12-12": return "BLOCK_REVISION"
        return "PASS" if c["pp1656_listed"] else "BLOCK_CURRENT_ROUTE_EVIDENCE"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 54
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 18
    assert len(model["temporal_model"]) == 2
    assert model["verified_structure"] == {
        "body_numbered_points": 21,
        "appendices": 13,
        "body_point5_function_groups": 13,
        "appendix1_function_groups": 16,
        "appendix4_commands": 17,
        "appendix7_kpd1_message_families": 12,
        "appendix9_kpd2_message_families": 9,
        "appendix10_numbered_points": 4,
    }
    assert model["verification_boundary"]["appendices3_to9_exact_command_message_byte_bit_and_code_tables"] == "PENDING_IMMUTABLE_PAGE_REVIEW"
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
    print("PASS: Order 645 mobile open core; 54 rules, 2 temporal routes, 18 evidence nodes, 21 body points, 13 appendices, 16 appendix-1 functions, 56 cases; exact byte tables pending")


if __name__ == "__main__": main()
