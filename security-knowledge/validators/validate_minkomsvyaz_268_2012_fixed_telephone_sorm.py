#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-268-2012/fixed-telephone-sorm-equipment-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-268-2012/fixed-telephone-sorm-equipment-regression-v1.json")


def evaluate(c):
    q = c["query"]
    if q == "scope":
        return "IN_SCOPE" if c["node"] in {"TRANSIT", "TERMINAL_TRANSIT", "TERMINAL"} and c["technology"] in {"CIRCUIT", "PACKET"} and c["network"] in {"PUBLIC_FIXED", "DEDICATED_FIXED"} else "OUT_OF_SCOPE"
    if q == "decision":
        if not c["orm_decision"]: return "BLOCK_MISSING_ORM_DECISION"
        return "PASS" if c["subscriber"] else "BLOCK_NOT_CONTROL_OBJECT"
    if q == "channels": return "PASS" if all(c[k] for k in ("kpd1_commands", "kpd1_responses", "kpd2_connections")) else "BLOCK_CHANNEL_ROLES"
    if q == "control_modes": return "PASS" if all(c[k] for k in ("statistical", "full", "combined", "separate")) else "BLOCK_CONTROL_MODE"
    if q == "unauthorized_monitoring": return "PASS" if all(c[k] for k in ("service_programs", "transport", "node_memory")) else "BLOCK_MONITORING_ROUTE"
    if q == "event_timing":
        if c.get("treat_as_retention"): return "BLOCK_UNIT_SEMANTICS"
        return "PASS" if c["milliseconds"] <= 200 else "BLOCK_EVENT_PORT_LATENCY"
    if q == "concealment":
        if c["operator_logs_reveal"]: return "BLOCK_OPERATOR_LOG_DISCLOSURE"
        return "BLOCK_PARTICIPANT_DETECTION" if c["participants_detect"] else "PASS"
    if q == "appendix_topology": return "PASS" if (c["appendices"], c["body_points"]) == (12, 19) else "BLOCK_STRUCTURE"
    if q == "kpd_variants": return "PASS" if c["variants"] == 2 and c["x25"] and c["ethernet_tcp_ip"] else "BLOCK_KPD_VARIANTS"
    if q == "x25_failover": return "PASS" if all(c[k] for k in ("health_monitored", "auto_next_pair", "unsent_destroyed", "voice_not_blocked", "valid_command_recovery")) else "BLOCK_X25_FAILOVER"
    if q == "tcp_packet": return "PASS" if c["ports"] == 2 and c["header_first"] and not c["split"] else "BLOCK_TCP_PACKET_ROUTE"
    if q == "control_change_time":
        if c["node"] in {"TERMINAL", "TERMINAL_TRANSIT"} and c["protocol"] != "X25": return "NOT_STATED_COMBINATION"
        if c["node"] == "TRANSIT" and c["protocol"] not in {"X25", "TCP_IP"}: return "NOT_STATED_COMBINATION"
        return "PASS" if c["seconds"] <= 15 else "BLOCK_CONTROL_CHANGE_TIME"
    if q == "legal_authority":
        if not c["orm_decision"]: return "BLOCK_MISSING_LAWFUL_BASIS"
        return "PASS" if c["technical_capability"] else "BLOCK_TECHNICAL_CAPABILITY"
    if q == "byte_table":
        if c["claim_exact"] and not c["immutable_review"]: return "BLOCK_UNVERIFIED_BYTE_CLAIM"
        if c["claim_exact"]: return "PASS_IF_REVIEW_ARTIFACT_BOUND"
        return "PENDING_FAIL_CLOSED"
    if q == "current_status":
        if c["revision"] != "2012-11-19": return "BLOCK_REVISION"
        return "PASS" if c["pp1656_listed"] else "BLOCK_CURRENT_ROUTE_EVIDENCE"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 50
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 16
    assert len(model["temporal_model"]) == 2
    assert model["verified_structure"] == {"body_numbered_points": 19, "appendices": 12, "body_point4_function_groups": 14, "appendix1_numbered_points": 6, "appendix11_message_families": 7}
    assert model["verification_boundary"]["appendix5_to11_exact_byte_command_message_and_bit_tables"] == "PENDING_IMMUTABLE_PAGE_REVIEW"
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
    print("PASS: Order 268 fixed-telephone open core; 50 rules, 2 temporal routes, 16 evidence nodes, 19 body points, 12 appendices, 14 function groups, 56 cases; exact byte tables pending")


if __name__ == "__main__": main()
