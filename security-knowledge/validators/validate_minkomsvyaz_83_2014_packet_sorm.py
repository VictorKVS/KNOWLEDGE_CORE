#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-83-2014/packet-switching-sorm-current-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-83-2014/packet-switching-sorm-current-regression-v1.json")

INPUT_MIN = {"I": 100, "II": 400, "III": 900, "IV": 4000, "V": 9000, "VI": 20000, "VII": 100000}


def evaluate(c):
    q = c["query"]
    if q == "scope":
        return "PASS" if c["network"] in {"PUBLIC", "DEDICATED"} and c["service"] in {"TELEMATIC", "VOICE_DATA", "NONVOICE_DATA"} else "BLOCK_SCOPE"
    if q == "version":
        d = date.fromisoformat(c["date"])
        if d < date(2014, 7, 29): return "PRE_ORDER83"
        if d < date(2019, 7, 14): return "ORDER83_ORIGINAL"
        return "ORDER83_ORDER139_CURRENT"
    if q == "historical_deadline": return "BLOCK_NOT_RECURRING" if c["recurring"] else "HISTORICAL_ONE_TIME"
    if q == "control_points":
        if c["count"] != 16: return "BLOCK_CONTROL_POINT_COUNT"
        if c["head"] != 1: return "BLOCK_HEAD_COUNT"
        return "PASS" if c["interface"] == "ETHERNET_IEEE_802_3_TX" else "BLOCK_MANAGEMENT_INTERFACE"
    if q == "control_parameters": return "PASS" if c["count"] == 20 else "BLOCK_PRE139_SET"
    if q == "control_capacity": return "PASS" if c["values"] >= 2000 else "BLOCK_CAPACITY"
    if q == "volatile_buffer":
        if c["treat_as_retention"]: return "BLOCK_NOT_RETENTION"
        return "PASS" if c["gib"] >= 2 else "BLOCK_BUFFER_SIZE"
    if q == "filter":
        if c["criteria"] > 2000: return "BLOCK_FILTER_CAPACITY"
        if c["types"] != 10: return "BLOCK_FILTER_TYPE_SET"
        if not c["head_filters_present"]: return "TRANSFER_FULL_VOLUME"
        return "EXCLUDE_MATCHING_MESSAGE" if c["matching_message"] else "TRANSFER_MESSAGE"
    if q == "failure": return "DELETE_PARAMETERS_AND_SELECTED_INFORMATION"
    if q == "email_selection": return "BLOCK_CRYPTOGRAPHIC_EXTENSION" if c["encrypted"] else "IN_SCOPE"
    if q == "class":
        cls = c["class"]
        if cls not in INPUT_MIN: return "BLOCK_UNKNOWN_CLASS"
        if c["input"] < INPUT_MIN[cls]: return "BLOCK_INPUT"
        if cls in {"I", "II", "III"}: ok = c["output"] >= c["input"] * 0.05
        elif cls in {"IV", "V"}: ok = c["output"] > 100
        else: ok = c["output"] > 1000
        return "PASS" if ok else "BLOCK_OUTPUT"
    if q == "monitor":
        return "PRESERVE_NONVOLATILE_AND_SEND_AFTER_RECONNECT" if c.get("offline") else "REPORT_HEAD_CONTROL_POINT"
    if q == "egress": return "PASS" if c["payload"] == "MAC_IDENTIFIER" else "BLOCK_NETWORK_EGRESS"
    if q == "interface_tension": return "BLOCK_INVENTED_RESOLUTION" if c["invent_exception"] else "PENDING_FAIL_CLOSED"
    if q == "hardware":
        if c["affects_network"]: return "BLOCK_NETWORK_IMPACT"
        return "PASS" if c["locked_case"] else "BLOCK_UNLOCKED_CASE"
    if q == "protocol": return "PASS" if c["control_and_data_separate"] and c["tcp_ip"] else "BLOCK_PROTOCOL_COLLAPSE"
    if q == "port": return "PASS" if c["channel"] == 0 and c["port"] in {16117, 16118} else "BLOCK_CHANNEL0_PORT"
    if q == "message_header": return "PASS" if (c["cod"], c["ident"], c["length"], c["data_formula"]) == (1, 2, 4, "LENGTH_MINUS_7") else "BLOCK_HEADER"
    if q == "historical_ring_buffer": return "BLOCK_DELETED_BY_ORDER139" if c["claim_current"] else "HISTORICAL_ONLY"
    if q == "deep_table": return "BLOCK_UNVERIFIED_DEEP_TABLE" if c["claim_exact"] and not c["immutable_page_review"] else "PASS_IF_ARTIFACT_BOUND"
    raise AssertionError(q)


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({x["id"] for x in model["atomic_rules"]}) == 47
    assert len(model["temporal_model"]) == 4
    assert len(model["evidence_model"]) == len({x["id"] for x in model["evidence_model"]}) == 18
    assert model["sources"]["revision_effective_from"] == "2019-07-14"
    assert model["current_point4"]["control_points"]["count"] == 16
    assert model["current_point4"]["control_parameters"]["count"] == 20
    assert model["current_point4"]["is_bd_orm_content"]["max_filter_criteria"] == 2000
    assert len(model["class_table"]) == 7
    assert model["interface_and_hardware_guards"]["appendix1"]["interface_entries"] == 25
    assert model["protocol_open_core"]["common_message_header"]["total_service_bytes"] == 7
    assert model["historical_delta_guard"]["rule"] == "NEVER_APPLY_DELETED_TWELVE_HOUR_RING_BUFFER_AS_CURRENT_REQUIREMENT"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 60
    failures = []
    for c in fixtures["cases"]:
        actual = evaluate(c)
        if actual != c["expected"]: failures.append((c["id"], c["expected"], actual))
    if failures:
        for f in failures: print("FAIL", f)
        raise SystemExit(1)
    print("PASS: Order 83 current packet SORM; 47 rules, 4 temporal routes, 18 evidence nodes, 60 cases; Order 139 delta applied; deleted 12-hour ring-buffer route blocked")


if __name__ == "__main__": main()
